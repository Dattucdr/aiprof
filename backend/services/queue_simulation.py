from datetime import datetime, timedelta, timezone
import random

from models.patient import Patient
from models.encounter import Encounter
from models.queue_item import QueueItem
from models.campaign import Campaign


OUTCOMES = [
    "NO_ANSWER",
    "BUSY",
    "VOICEMAIL",
    "DROPPED",
    "CONNECTED"
]


def create_simulation_patients(
    hospital_id: int,
    campaign_id: int,
    db,
    count: int = 25
):
    """
    Create development-only patients, encounters and queue items
    for testing queue behavior.
    """

    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.id == campaign_id,
            Campaign.hospital_id == hospital_id
        )
        .first()
    )

    if not campaign:
        raise ValueError("Campaign not found")

    created_patients = []

    now = datetime.now(timezone.utc)

    for index in range(count):

        patient = Patient(
            hospital_id=hospital_id,
            medical_record_number=f"SIM-{index + 1:04d}",
            first_name=f"Test{index + 1}",
            last_name="Patient",
            phone_number=f"900000{index + 1:04d}",
            communication_consent=True,
            preferred_language="English",
            preferred_call_time="16:00"
        )

        db.add(patient)
        db.flush()

        # Different discharge dates create different deadline pressures.
        discharge_datetime = (
            now - timedelta(
                days=random.randint(1, 6)
            )
        )

        encounter = Encounter(
            patient_id=patient.id,
            hospital_id=hospital_id,
            encounter_type="INPATIENT",
            admission_datetime=(
                discharge_datetime -
                timedelta(days=random.randint(1, 5))
            ),
            discharge_datetime=discharge_datetime,
            discharge_status="DISCHARGED",
            reason="Simulation encounter",
            discharge_instructions="Simulation follow-up instructions"
        )

        db.add(encounter)

        queue_item = QueueItem(
            hospital_id=hospital_id,
            campaign_id=campaign_id,
            patient_id=patient.id,
            status="PENDING",
            deadline_at=(
                discharge_datetime +
                timedelta(days=campaign.follow_up_window_days)
            ),
            attempt_count=0
        )

        db.add(queue_item)

        created_patients.append(patient)

    db.commit()

    return created_patients


def simulate_call_outcome(
    queue_item: QueueItem,
    hospital,
    db
):
    """
    Simulate one outbound call result.
    """

    from services.queue_service import handle_call_outcome

    outcome = random.choice(OUTCOMES)

    if outcome == "CONNECTED":

        queue_item.status = "COMPLETED"
        queue_item.worker_id = None
        queue_item.locked_at = None
        queue_item.worker_heartbeat_at = None

        db.commit()
        db.refresh(queue_item)

        return outcome

    handle_call_outcome(
        queue_item=queue_item,
        outcome=outcome,
        hospital=hospital,
        db=db
    )

    return outcome


def run_queue_simulation(
    hospital_id: int,
    worker_count: int,
    db,
    max_iterations: int = 100
):
    """
    Simulate multiple workers processing queue items.
    """

    from models.hospital import Hospital
    from services.queue_service import dispatch_next_queue_item

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    if not hospital:
        raise ValueError("Hospital not found")

    processed = []

    for iteration in range(max_iterations):

        worker_id = (
            f"simulation-worker-"
            f"{(iteration % worker_count) + 1}"
        )

        queue_item = dispatch_next_queue_item(
            hospital_id=hospital_id,
            worker_id=worker_id,
            db=db
        )

        if not queue_item:
            break

        outcome = simulate_call_outcome(
            queue_item=queue_item,
            hospital=hospital,
            db=db
        )

        processed.append({
            "queue_item_id": queue_item.id,
            "patient_id": queue_item.patient_id,
            "worker_id": worker_id,
            "outcome": outcome,
            "attempt_count": queue_item.attempt_count
        })

    return processed

