from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.database import get_db
from models.outreach_documentation import OutreachDocumentation
from services.ehr_documentation_service import (
    write_outreach_note_to_mock_ehr,
)

router = APIRouter(
    prefix="/ehr",
    tags=["Mock EHR Integration"]
)


@router.post(
    "/documentation/{documentation_id}/write"
)
def write_documentation_to_ehr(
    documentation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documentation = (
        db.query(OutreachDocumentation)
        .filter(
            OutreachDocumentation.id == documentation_id,
            OutreachDocumentation.hospital_id
            == current_user.hospital_id,
        )
        .first()
    )

    if not documentation:
        raise HTTPException(
            status_code=404,
            detail="Documentation not found",
        )

    result = write_outreach_note_to_mock_ehr(
        db=db,
        hospital_id=current_user.hospital_id,
        patient_id=documentation.patient_id,
        documentation=documentation,
    )

    return result


@router.get("/documentation/call/{call_id}")
def read_call_documentation(
    call_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = (
        db.query(OutreachDocumentation)
        .filter(
            OutreachDocumentation.call_id == call_id,
            OutreachDocumentation.hospital_id == current_user.hospital_id,
        )
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Documentation not found for call",
        )

    return {
        "id": doc.id,
        "hospital_id": doc.hospital_id,
        "patient_id": doc.patient_id,
        "call_id": doc.call_id,
        "triage_assessment_id": doc.triage_assessment_id,
        "consensus_assessment_id": doc.consensus_assessment_id,
        "escalation_id": doc.escalation_id,
        "summary": doc.summary,
        "symptoms": doc.symptoms,
        "medication_concerns": doc.medication_concerns,
        "patient_questions": doc.patient_questions,
        "red_flags": doc.red_flags,
        "triage_risk_level": doc.triage_risk_level,
        "recommended_action": doc.recommended_action,
        "escalation_created": doc.escalation_created,
        "escalation_reason": doc.escalation_reason,
        "follow_up_required": doc.follow_up_required,
        "follow_up_notes": doc.follow_up_notes,
        "created_at": doc.created_at,
    }


@router.get("/documentation/{documentation_id}")
def read_documentation(
    documentation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = (
        db.query(OutreachDocumentation)
        .filter(
            OutreachDocumentation.id == documentation_id,
            OutreachDocumentation.hospital_id == current_user.hospital_id,
        )
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Documentation not found",
        )

    return {
        "id": doc.id,
        "hospital_id": doc.hospital_id,
        "patient_id": doc.patient_id,
        "call_id": doc.call_id,
        "triage_assessment_id": doc.triage_assessment_id,
        "consensus_assessment_id": doc.consensus_assessment_id,
        "escalation_id": doc.escalation_id,
        "summary": doc.summary,
        "symptoms": doc.symptoms,
        "medication_concerns": doc.medication_concerns,
        "patient_questions": doc.patient_questions,
        "red_flags": doc.red_flags,
        "triage_risk_level": doc.triage_risk_level,
        "recommended_action": doc.recommended_action,
        "escalation_created": doc.escalation_created,
        "escalation_reason": doc.escalation_reason,
        "follow_up_required": doc.follow_up_required,
        "follow_up_notes": doc.follow_up_notes,
        "created_at": doc.created_at,
    }


