from datetime import datetime, timezone

from fastapi import HTTPException

from models.call import Call
from models.queue_item import QueueItem
from models.campaign import Campaign
from models.patient import Patient


from services.queue_service import transition_queue_item


def create_call(
    queue_item: QueueItem,
    worker_id: str,
    idempotency_key: str,
    db
):
    """
    Create a structured call attempt for a reserved queue item.
    """

    if queue_item.status != "CALLING":
        raise HTTPException(
            status_code=400,
            detail="Queue item is not in CALLING state"
        )

    existing_call = (
        db.query(Call)
        .filter(
            Call.idempotency_key == idempotency_key
        )
        .first()
    )

    if existing_call:
        return existing_call

    call = Call(
        hospital_id=queue_item.hospital_id,
        campaign_id=queue_item.campaign_id,
        patient_id=queue_item.patient_id,
        queue_item_id=queue_item.id,
        attempt_number=queue_item.attempt_count,
        status="IN_PROGRESS",
        worker_id=worker_id,
        started_at=datetime.now(timezone.utc),
        idempotency_key=idempotency_key
    )

    db.add(call)
    db.commit()
    db.refresh(call)

    return call

def finish_call(
    call: Call,
    outcome: str,
    notes: str | None,
    transcript: str | None,
    db
):
    allowed_outcomes = {
        "CONNECTED",
        "NO_ANSWER",
        "BUSY",
        "VOICEMAIL",
        "DROPPED",
        "FAILED"
    }

    if outcome not in allowed_outcomes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid call outcome: {outcome}"
        )

    if call.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="Call is already finished"
        )

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # Update call record
    # ---------------------------------------------------------

    call.outcome = outcome
    call.notes = notes
    call.transcript = transcript
    call.ended_at = now

    if call.started_at:
        started_at = call.started_at

        if started_at.tzinfo is None:
            started_at = started_at.replace(
                tzinfo=timezone.utc
            )

        call.duration_seconds = max(
            0,
            int((now - started_at).total_seconds())
        )

    call.status = "COMPLETED"

    # ---------------------------------------------------------
    # Update queue record
    # ---------------------------------------------------------

    queue_item = (
        db.query(QueueItem)
        .filter(
            QueueItem.id == call.queue_item_id,
            QueueItem.hospital_id == call.hospital_id
        )
        .with_for_update()
        .first()
    )

    if not queue_item:
        raise HTTPException(
            status_code=404,
            detail="Associated queue item not found"
        )

    if outcome == "CONNECTED":
        transition_queue_item(queue_item, "CONNECTED")

    elif outcome in {
        "NO_ANSWER",
        "BUSY",
        "VOICEMAIL",
        "DROPPED"
    }:
        transition_queue_item(queue_item, outcome)

    elif outcome == "FAILED":
        transition_queue_item(queue_item, "FAILED")

    # Worker is no longer holding the queue item.
    queue_item.worker_id = None
    queue_item.locked_at = None
    queue_item.worker_heartbeat_at = None

    db.commit()

    db.refresh(call)
    db.refresh(queue_item)

    return call