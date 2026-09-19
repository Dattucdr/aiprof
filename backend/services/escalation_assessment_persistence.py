import json

from sqlalchemy.orm import Session

from models.escalation_assessment import (
    EscalationAssessment,
)


def save_assessment(
    db: Session,
    hospital_id: int,
    patient_id: int,
    call_id: int,
    queue_item_id: int | None,
    assessment,
):
    existing = (
        db.query(EscalationAssessment)
        .filter(
            EscalationAssessment.hospital_id
            == hospital_id,

            EscalationAssessment.call_id
            == call_id,

            EscalationAssessment.assessor
            == assessment.assessor,
        )
        .first()
    )

    if existing:
        return existing

    record = EscalationAssessment(
        hospital_id=hospital_id,
        patient_id=patient_id,
        call_id=call_id,
        queue_item_id=queue_item_id,

        assessor=assessment.assessor,

        risk_level=assessment.risk_level,

        recommended_action=(
            assessment.recommended_action
        ),

        evidence=json.dumps(
            assessment.evidence
        ),

        red_flags=json.dumps(
            assessment.red_flags
        ),

        confidence=assessment.confidence,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
