from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from models.queue_item import QueueItem
from models.hospital import Hospital
from models.campaign import Campaign


ALLOWED_TRANSITIONS = {
    "PENDING": [
        "SCHEDULED",
        "CALLING",
        "FAILED"
    ],

    "SCHEDULED": [
        "CALLING",
        "CANCELLED",
        "FAILED"
    ],

    "CALLING": [
        "CONNECTED",
        "NO_ANSWER",
        "BUSY",
        "VOICEMAIL",
        "DROPPED",
        "FAILED"
    ],

    "CONNECTED": [
        "COMPLETED",
        "ESCALATED",
        "CALLBACK_SCHEDULED",
        "MANUAL_FOLLOW_UP",
        "FAILED"
    ],

    "NO_ANSWER": [
        "RETRY_SCHEDULED",
        "MANUAL_FOLLOW_UP"
    ],

    "BUSY": [
        "RETRY_SCHEDULED",
        "MANUAL_FOLLOW_UP"
    ],

    "VOICEMAIL": [
        "RETRY_SCHEDULED",
        "MANUAL_FOLLOW_UP"
    ],

    "DROPPED": [
        "RETRY_SCHEDULED",
        "MANUAL_FOLLOW_UP"
    ],

    "RETRY_SCHEDULED": [
        "CALLING",
        "MANUAL_FOLLOW_UP",
        "FAILED"
    ],

    "CALLBACK_SCHEDULED": [
        "CALLING",
        "MANUAL_FOLLOW_UP",
        "FAILED"
    ],

    "ESCALATED": [
        "MANUAL_FOLLOW_UP",
        "COMPLETED"
    ],

    "MANUAL_FOLLOW_UP": [
        "COMPLETED",
        "FAILED"
    ],

    "COMPLETED": [],

    "FAILED": [],

    "CANCELLED": []
}


def transition_queue_item(
    queue_item: QueueItem,
    new_status: str
):
    current_status = queue_item.status

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid queue transition: "
                f"{current_status} -> {new_status}"
            )
        )

    queue_item.status = new_status

    return queue_item


def is_within_calling_hours(hospital, current_time=None):
    """
    Check whether outbound calling is currently allowed
    according to the hospital's configured timezone and
    calling hours.
    """

    if current_time is None:
        current_time = datetime.now(timezone.utc)

    try:
        hospital_timezone = ZoneInfo(hospital.timezone)
    except Exception:
        return False

    local_time = current_time.astimezone(hospital_timezone).time()

    start_time = time.fromisoformat(
        hospital.calling_start_time
    )

    end_time = time.fromisoformat(
        hospital.calling_end_time
    )

    return start_time <= local_time <= end_time


def get_deadline_pressure(queue_item):
    """
    Calculate deadline pressure for queue prioritization.
    """

    if not queue_item.deadline_at:
        return 0

    now = datetime.now(timezone.utc)

    deadline = queue_item.deadline_at

    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    hours_remaining = (
        deadline - now
    ).total_seconds() / 3600

    if hours_remaining <= 0:
        return 100

    if hours_remaining <= 6:
        return 80

    if hours_remaining <= 24:
        return 60

    if hours_remaining <= 48:
        return 40

    return 20


def calculate_aging_bonus(queue_item):
    """
    Increase priority gradually while an item waits in the queue.

    This prevents low-priority work from waiting indefinitely.
    """

    if not queue_item.created_at:
        return 0.0

    now = datetime.now(timezone.utc)

    created_at = queue_item.created_at

    if created_at.tzinfo is None:
        created_at = created_at.replace(
            tzinfo=timezone.utc
        )

    waiting_hours = (
        now - created_at
    ).total_seconds() / 3600

    # +2 points for every waiting hour,
    # capped so aging cannot completely dominate safety/deadline factors.
    return min(waiting_hours * 2, 30)


def calculate_priority_score(campaign, patient, queue_item):
    score = 0.0

    # Campaign priority
    score += max(0, 10 - campaign.priority) * 5

    # Deadline pressure
    score += get_deadline_pressure(queue_item) * 0.5

    # Aging / fairness
    score += calculate_aging_bonus(queue_item)

    # Callback urgency
    if queue_item.callback_at:
        now = datetime.now(timezone.utc)

        callback = queue_item.callback_at

        if callback.tzinfo is None:
            callback = callback.replace(
                tzinfo=timezone.utc
            )

        if callback <= now:
            score += 45
        else:
            score += 20

    # Retry priority
    if queue_item.status == "RETRY_SCHEDULED":
        score += 15

    # Previous failed attempts
    score += min(
        queue_item.attempt_count * 3,
        15
    )

    # Patient availability
    if patient.preferred_call_time:
        score += 5

    return round(score, 2)



def create_queue_items_for_campaign(
    campaign,
    hospital_id,
    db
):
    from models.patient import Patient
    from models.encounter import Encounter
    from services.eligibility import check_patient_eligibility
    from datetime import datetime, timedelta, timezone

    patients = db.query(Patient).filter(
        Patient.hospital_id == hospital_id,
        Patient.is_active == True
    ).all()

    created_items = []
    skipped_items = []

    for patient in patients:

        result = check_patient_eligibility(
            patient=patient,
            campaign=campaign,
            db=db
        )

        if not result["eligible"]:
            continue

        existing_item = db.query(QueueItem).filter(
            QueueItem.hospital_id == hospital_id,
            QueueItem.campaign_id == campaign.id,
            QueueItem.patient_id == patient.id
        ).first()

        if existing_item:
            skipped_items.append(patient.id)
            continue

        encounter = (
            db.query(Encounter)
            .filter(
                Encounter.patient_id == patient.id,
                Encounter.hospital_id == hospital_id,
                Encounter.discharge_datetime.is_not(None)
            )
            .order_by(
                Encounter.discharge_datetime.desc()
            )
            .first()
        )

        if not encounter:
            continue

        discharge_datetime = encounter.discharge_datetime

        if discharge_datetime.tzinfo is None:
            discharge_datetime = discharge_datetime.replace(
                tzinfo=timezone.utc
            )

        deadline_at = (
            discharge_datetime +
            timedelta(days=campaign.follow_up_window_days)
        )

        queue_item = QueueItem(
            hospital_id=hospital_id,
            campaign_id=campaign.id,
            patient_id=patient.id,
            status="PENDING",
            deadline_at=deadline_at,
            attempt_count=0
        )

        db.add(queue_item)
        db.flush()

        queue_item.priority_score = calculate_priority_score(
            campaign=campaign,
            patient=patient,
            queue_item=queue_item
        )

        created_items.append(queue_item)

    db.commit()

    for item in created_items:
        db.refresh(item)

    return {
        "created_items": created_items,
        "skipped_patient_ids": skipped_items
    }


def get_active_call_count(
    hospital_id: int,
    db
):
    active_statuses = [
        "CALLING",
        "CONNECTED"
    ]

    count = db.query(
        func.count(QueueItem.id)
    ).filter(
        QueueItem.hospital_id == hospital_id,
        QueueItem.status.in_(active_statuses)
    ).scalar()

    return count or 0


def has_available_capacity(
    hospital_id: int,
    db
):
    from models.hospital import Hospital

    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        return False

    active_calls = get_active_call_count(
        hospital_id,
        db
    )

    return active_calls < hospital.outbound_capacity


def reserve_queue_item(
    queue_item_id: int,
    hospital_id: int,
    worker_id: str,
    db
):
    queue_item = db.query(
        QueueItem
    ).filter(
        QueueItem.id == queue_item_id,
        QueueItem.hospital_id == hospital_id
    ).with_for_update().first()

    if not queue_item:
        return None

    if queue_item.status not in [
        "PENDING",
        "SCHEDULED",
        "RETRY_SCHEDULED",
        "CALLBACK_SCHEDULED"
    ]:
        return None

    if not has_available_capacity(
        hospital_id,
        db
    ):
        return None

    queue_item.status = "CALLING"
    queue_item.worker_id = worker_id
    now = datetime.now(timezone.utc)
    queue_item.locked_at = now
    queue_item.worker_heartbeat_at = now
    queue_item.attempt_count += 1

    db.commit()
    db.refresh(queue_item)

    return queue_item


def dispatch_next_queue_item(hospital_id: int, worker_id: str, db):
    """
    Select and reserve the highest-priority callable queue item.

    The hospital row is locked first so multiple workers cannot
    simultaneously exceed the hospital's outbound capacity.
    """
    from models.patient import Patient

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 1. Lock hospital row
    # ---------------------------------------------------------

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .with_for_update()
        .first()
    )

    if not hospital:
        db.rollback()
        return None

    if not is_within_calling_hours(hospital):
        db.rollback()
        return None

    # ---------------------------------------------------------
    # 2. Check active call capacity
    # ---------------------------------------------------------

    active_calls = (
        db.query(func.count(QueueItem.id))
        .filter(
            QueueItem.hospital_id == hospital_id,
            QueueItem.status.in_(["CALLING", "CONNECTED"])
        )
        .scalar()
    ) or 0

    if active_calls >= hospital.outbound_capacity:
        db.rollback()
        return None

    # ---------------------------------------------------------
    # 3. Find highest-priority callable queue items
    # ---------------------------------------------------------

    candidates = (
        db.query(QueueItem)
        .join(
            Campaign,
            Campaign.id == QueueItem.campaign_id
        )
        .filter(
            QueueItem.hospital_id == hospital_id,

            # Only active outbound states
            QueueItem.status.in_([
                "PENDING",
                "SCHEDULED",
                "RETRY_SCHEDULED",
                "CALLBACK_SCHEDULED"
            ]),

            # Only campaigns currently allowed to make calls
            Campaign.status == "RUNNING",

            # Scheduled work must be due
            or_(
                QueueItem.status == "PENDING",

                (
                    (QueueItem.status == "SCHEDULED") &
                    (
                        QueueItem.scheduled_at.is_(None) |
                        (QueueItem.scheduled_at <= now)
                    )
                ),

                (
                    (QueueItem.status == "RETRY_SCHEDULED") &
                    (
                        QueueItem.next_attempt_at.is_(None) |
                        (QueueItem.next_attempt_at <= now)
                    )
                ),

                (
                    (QueueItem.status == "CALLBACK_SCHEDULED") &
                    (
                        QueueItem.callback_at.is_(None) |
                        (QueueItem.callback_at <= now)
                    )
                )
            )
        )
        .order_by(
            QueueItem.priority_score.desc(),
            QueueItem.deadline_at.asc().nullslast(),
            QueueItem.created_at.asc()
        )
        .limit(20)
        .all()
    )

    # ---------------------------------------------------------
    # 4. Rank candidates with updated dynamic priority scores
    # ---------------------------------------------------------

    ranked_candidates = []

    for candidate in candidates:

        patient = (
            db.query(Patient)
            .filter(
                Patient.id == candidate.patient_id,
                Patient.hospital_id == hospital_id
            )
            .first()
        )

        campaign = (
            db.query(Campaign)
            .filter(
                Campaign.id == candidate.campaign_id,
                Campaign.hospital_id == hospital_id
            )
            .first()
        )

        if not patient or not campaign:
            continue

        current_score = calculate_priority_score(
            campaign=campaign,
            patient=patient,
            queue_item=candidate
        )

        ranked_candidates.append(
            (current_score, candidate, patient, campaign)
        )

    if not ranked_candidates:
        db.rollback()
        return None

    ranked_candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    top_score, queue_item, patient, campaign = ranked_candidates[0]

    queue_item.priority_score = calculate_priority_score(
        campaign=campaign,
        patient=patient,
        queue_item=queue_item
    )

    # ---------------------------------------------------------
    # 5. Reserve the queue item
    # ---------------------------------------------------------

    queue_item.status = "CALLING"
    queue_item.worker_id = worker_id
    queue_item.locked_at = now
    queue_item.worker_heartbeat_at = now
    queue_item.attempt_count += 1

    db.commit()
    db.refresh(queue_item)

    return queue_item


def calculate_retry_time(
    attempt_count: int,
    backoff_minutes: int
):
    """
    Exponential retry backoff.

    Attempt 1 -> backoff * 1
    Attempt 2 -> backoff * 2
    Attempt 3 -> backoff * 4
    """

    multiplier = 2 ** max(attempt_count - 1, 0)

    delay_minutes = backoff_minutes * multiplier

    return datetime.now(timezone.utc) + timedelta(
        minutes=delay_minutes
    )


def schedule_retry(queue_item: QueueItem, hospital, db):
    """
    Schedule another attempt or move the item to manual follow-up
    when the maximum retry count has been reached.
    """

    max_attempts = hospital.max_retry_attempts

    if queue_item.attempt_count >= max_attempts:
        queue_item.status = "MANUAL_FOLLOW_UP"
        queue_item.next_attempt_at = None
        queue_item.worker_id = None
        queue_item.locked_at = None
        queue_item.worker_heartbeat_at = None

        db.commit()
        db.refresh(queue_item)

        return queue_item

    queue_item.status = "RETRY_SCHEDULED"

    queue_item.next_attempt_at = calculate_retry_time(
        attempt_count=queue_item.attempt_count,
        backoff_minutes=hospital.retry_backoff_minutes
    )

    queue_item.worker_id = None
    queue_item.locked_at = None
    queue_item.worker_heartbeat_at = None

    db.commit()
    db.refresh(queue_item)

    return queue_item


RETRYABLE_OUTCOMES = {
    "NO_ANSWER",
    "BUSY",
    "VOICEMAIL",
    "DROPPED"
}


def handle_call_outcome(
    queue_item: QueueItem,
    outcome: str,
    hospital,
    db
):
    """
    Process the result of an outbound call.
    """

    if outcome not in RETRYABLE_OUTCOMES:
        raise ValueError(
            f"Unsupported retry outcome: {outcome}"
        )

    queue_item.status = outcome

    db.commit()
    db.refresh(queue_item)

    return schedule_retry(
        queue_item=queue_item,
        hospital=hospital,
        db=db
    )


def schedule_callback(
    queue_item: QueueItem,
    callback_at: datetime,
    db
):
    """
    Schedule a patient-requested callback.
    """

    now = datetime.now(timezone.utc)

    if callback_at.tzinfo is None:
        callback_at = callback_at.replace(
            tzinfo=timezone.utc
        )

    if callback_at <= now:
        raise ValueError(
            "Callback time must be in the future"
        )

    queue_item.status = "CALLBACK_SCHEDULED"
    queue_item.callback_at = callback_at

    queue_item.next_attempt_at = None
    queue_item.worker_id = None
    queue_item.locked_at = None
    queue_item.worker_heartbeat_at = None

    db.commit()
    db.refresh(queue_item)

    return queue_item


STALE_CALL_TIMEOUT_MINUTES = 10


def recover_stale_queue_items(hospital_id: int, db):
    """
    Recover queue items whose workers stopped processing them.
    """

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    if not hospital:
        return []

    now = datetime.now(timezone.utc)

    stale_before = (
        now -
        timedelta(minutes=STALE_CALL_TIMEOUT_MINUTES)
    )

    stale_items = (
        db.query(QueueItem)
        .filter(
            QueueItem.hospital_id == hospital_id,
            QueueItem.status == "CALLING",
            or_(
                QueueItem.worker_heartbeat_at < stale_before,
                (
                    QueueItem.worker_heartbeat_at.is_(None) &
                    QueueItem.locked_at.is_not(None) &
                    (QueueItem.locked_at < stale_before)
                )
            )
        )
        .with_for_update(skip_locked=True)
        .all()
    )

    recovered_items = []

    for queue_item in stale_items:

        if queue_item.attempt_count >= hospital.max_retry_attempts:
            queue_item.status = "MANUAL_FOLLOW_UP"
            queue_item.next_attempt_at = None

        else:
            queue_item.status = "RETRY_SCHEDULED"
            queue_item.next_attempt_at = now

        queue_item.worker_id = None
        queue_item.locked_at = None
        queue_item.worker_heartbeat_at = None

        recovered_items.append(queue_item)

    db.commit()

    for item in recovered_items:
        db.refresh(item)

    return recovered_items







