import json

from sqlalchemy.orm import Session

from models.triage_assessment import TriageAssessment
from ai.schemas.triage import TriageResult


def create_triage_assessment(
    db: Session,
    hospital_id: int,
    patient_id: int,
    triage_result: TriageResult | dict,
    call_id: int | None = None,
    queue_item_id: int | None = None,
    source: str = "AI"
) -> TriageAssessment:
    if isinstance(triage_result, TriageResult):
        risk_level = triage_result.risk_level
        recommended_action = triage_result.recommended_action
        evidence = json.dumps(triage_result.evidence)
        red_flags = json.dumps(triage_result.red_flags)
        confidence = triage_result.confidence
    else:
        risk_level = triage_result.get("risk_level")
        recommended_action = triage_result.get("recommended_action")
        evidence = json.dumps(triage_result.get("evidence", []))
        red_flags = json.dumps(triage_result.get("red_flags", []))
        confidence = triage_result.get("confidence", 1.0)

    assessment = TriageAssessment(
        hospital_id=hospital_id,
        patient_id=patient_id,
        call_id=call_id,
        queue_item_id=queue_item_id,
        risk_level=risk_level,
        recommended_action=recommended_action,
        evidence=evidence,
        red_flags=red_flags,
        confidence=confidence,
        source=source
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment


def get_triage_assessment(
    db: Session,
    hospital_id: int,
    assessment_id: int
):
    assessment = (
        db.query(TriageAssessment)
        .filter(
            TriageAssessment.id == assessment_id,
            TriageAssessment.hospital_id == hospital_id
        )
        .first()
    )

    if not assessment:
        raise ValueError("Triage assessment not found")

    return assessment


def get_call_triage_assessment(
    db: Session,
    hospital_id: int,
    call_id: int
):
    return (
        db.query(TriageAssessment)
        .filter(
            TriageAssessment.hospital_id == hospital_id,
            TriageAssessment.call_id == call_id
        )
        .order_by(TriageAssessment.created_at.desc())
        .first()
    )


def get_patient_triage_history(
    db: Session,
    hospital_id: int,
    patient_id: int
):
    assessments = (
        db.query(TriageAssessment)
        .filter(
            TriageAssessment.hospital_id == hospital_id,
            TriageAssessment.patient_id == patient_id
        )
        .order_by(TriageAssessment.created_at.desc())
        .all()
    )

    return assessments


def assessment_to_dict(assessment):

    return {
        "id": assessment.id,
        "hospital_id": assessment.hospital_id,
        "patient_id": assessment.patient_id,
        "call_id": assessment.call_id,
        "queue_item_id": assessment.queue_item_id,
        "risk_level": assessment.risk_level,
        "recommended_action": assessment.recommended_action,
        "evidence": json.loads(assessment.evidence or "[]"),
        "red_flags": json.loads(assessment.red_flags or "[]"),
        "confidence": assessment.confidence,
        "source": assessment.source,
        "created_at": assessment.created_at,
    }
