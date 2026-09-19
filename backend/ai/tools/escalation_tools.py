from sqlalchemy.orm import Session

from models.escalation import Escalation
from models.patient import Patient
from models.queue_item import QueueItem
from ai.tools.validators import (
    validate_patient_id,
    validate_hospital_id,
    validate_escalation_priority,
    validate_required_text
)

def create_ai_escalation(
    db: Session,
    hospital_id: int,
    patient_id: int,
    queue_item_id: int | None,
    reason: str,
    priority: str,
    evidence: str | None = None
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)
    validate_escalation_priority(priority)

    reason = validate_required_text(reason, "reason")
    if evidence is not None:
        evidence = validate_required_text(evidence, "evidence")

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.hospital_id == hospital_id
        )
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    if queue_item_id is not None:
        queue_item = (
            db.query(QueueItem)
            .filter(
                QueueItem.id == queue_item_id,
                QueueItem.hospital_id == hospital_id,
                QueueItem.patient_id == patient_id
            )
            .first()
        )
        if not queue_item:
            raise ValueError("Queue item not found")

    escalation = Escalation(
        hospital_id=hospital_id,
        patient_id=patient_id,
        queue_item_id=queue_item_id,
        reason=reason,
        priority=priority,
        evidence=evidence,
        status="OPEN",
        source="AI"
    )

    db.add(escalation)
    db.commit()
    db.refresh(escalation)

    return {
        "escalation_id": escalation.id,
        "hospital_id": escalation.hospital_id,
        "patient_id": escalation.patient_id,
        "queue_item_id": escalation.queue_item_id,
        "reason": escalation.reason,
        "priority": escalation.priority,
        "evidence": escalation.evidence,
        "status": escalation.status,
        "source": escalation.source,
        "created_at": escalation.created_at,
    }
