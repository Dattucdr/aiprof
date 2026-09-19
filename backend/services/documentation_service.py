import json

from sqlalchemy.orm import Session

from models.outreach_documentation import OutreachDocumentation


def create_documentation(
    db: Session,
    hospital_id: int,
    patient_id: int,
    call_id: int,
    triage_assessment_id: int | None,
    consensus_assessment_id: int | None,
    escalation_id: int | None,
    documentation,
):
    existing = (
        db.query(OutreachDocumentation)
        .filter(
            OutreachDocumentation.hospital_id == hospital_id,
            OutreachDocumentation.call_id == call_id,
        )
        .first()
    )

    if existing:
        return existing

    record = OutreachDocumentation(
        hospital_id=hospital_id,
        patient_id=patient_id,
        call_id=call_id,

        triage_assessment_id=triage_assessment_id,
        consensus_assessment_id=consensus_assessment_id,
        escalation_id=escalation_id,

        summary=documentation.summary,

        symptoms=json.dumps(
            documentation.symptoms
        ),

        medication_concerns=json.dumps(
            documentation.medication_concerns
        ),

        patient_questions=json.dumps(
            documentation.patient_questions
        ),

        red_flags=json.dumps(
            documentation.red_flags
        ),

        triage_risk_level=documentation.triage_risk_level,

        recommended_action=documentation.recommended_action,

        escalation_created=documentation.escalation_created,

        escalation_reason=documentation.escalation_reason,

        follow_up_required=documentation.follow_up_required,

        follow_up_notes=documentation.follow_up_notes,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
