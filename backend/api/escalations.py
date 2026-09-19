import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from auth.dependencies import get_current_user
from models.escalation import Escalation
from schemas.escalation import EscalationStatusUpdate
from services.escalation_service import (
    get_escalation,
    get_hospital_escalations,
    get_patient_escalations,
    update_escalation_status,
)


router = APIRouter(
    prefix="/escalations",
    tags=["Escalations"]
)


@router.get("")
def list_escalations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    escalations = get_hospital_escalations(
        db,
        current_user.hospital_id,
    )

    return [
        {
            "id": item.id,
            "hospital_id": item.hospital_id,
            "patient_id": item.patient_id,
            "queue_item_id": item.queue_item_id,
            "call_id": item.call_id,
            "consensus_assessment_id": item.consensus_assessment_id,
            "reason": item.reason,
            "priority": item.priority,
            "status": item.status,
            "source": item.source,
            "final_action": item.final_action,
            "created_at": item.created_at,
            "resolved_at": item.resolved_at,
            "resolution_notes": item.resolution_notes,
        }
        for item in escalations
    ]


@router.get("/call/{call_id}")
def read_call_escalation(
    call_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    escalation = (
        db.query(Escalation)
        .filter(
            Escalation.call_id == call_id,
            Escalation.hospital_id == current_user.hospital_id,
        )
        .first()
    )

    if not escalation:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found for call",
        )

    evidence_dict = {}
    if escalation.evidence:
        try:
            evidence_dict = json.loads(escalation.evidence)
        except Exception:
            evidence_dict = {"raw": escalation.evidence}

    return {
        "id": escalation.id,
        "hospital_id": escalation.hospital_id,
        "patient_id": escalation.patient_id,
        "queue_item_id": escalation.queue_item_id,
        "call_id": escalation.call_id,
        "consensus_assessment_id": escalation.consensus_assessment_id,
        "reason": escalation.reason,
        "priority": escalation.priority,
        "evidence": json.dumps(evidence_dict) if isinstance(evidence_dict, dict) else escalation.evidence,
        "status": escalation.status,
        "source": escalation.source,
        "final_action": escalation.final_action,
        "created_at": escalation.created_at,
        "updated_at": escalation.updated_at,
        "resolved_at": escalation.resolved_at,
        "resolution_notes": escalation.resolution_notes,
    }




@router.get("/{escalation_id}")
def read_escalation(
    escalation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    escalation = get_escalation(
        db,
        current_user.hospital_id,
        escalation_id,
    )

    if not escalation:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        )

    evidence_dict = {}
    if escalation.evidence:
        try:
            evidence_dict = json.loads(escalation.evidence)
        except Exception:
            evidence_dict = {"raw": escalation.evidence}

    result = {
        "id": escalation.id,
        "hospital_id": escalation.hospital_id,
        "patient_id": escalation.patient_id,
        "queue_item_id": escalation.queue_item_id,
        "call_id": escalation.call_id,
        "consensus_assessment_id": (
            escalation.consensus_assessment_id
        ),
        "reason": escalation.reason,
        "priority": escalation.priority,
        "evidence": evidence_dict,
        "status": escalation.status,
        "source": escalation.source,
        "final_action": escalation.final_action,
        "created_at": escalation.created_at,
        "updated_at": escalation.updated_at,
        "resolved_at": escalation.resolved_at,
        "resolution_notes": escalation.resolution_notes,
    }

    return result


@router.get("/patient/{patient_id}")
def read_patient_escalations(
    patient_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    escalations = get_patient_escalations(
        db,
        current_user.hospital_id,
        patient_id,
    )

    return [
        {
            "id": item.id,
            "patient_id": item.patient_id,
            "call_id": item.call_id,
            "consensus_assessment_id": (
                item.consensus_assessment_id
            ),
            "reason": item.reason,
            "priority": item.priority,
            "status": item.status,
            "final_action": item.final_action,
            "created_at": item.created_at,
            "resolved_at": item.resolved_at,
        }
        for item in escalations
    ]


@router.patch("/{escalation_id}/status")
def change_escalation_status(
    escalation_id: int,
    request: EscalationStatusUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    escalation = get_escalation(
        db,
        current_user.hospital_id,
        escalation_id,
    )

    if not escalation:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        )

    try:
        escalation = update_escalation_status(
            db,
            escalation,
            request.status,
            request.resolution_notes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    evidence_dict = {}
    if escalation.evidence:
        try:
            evidence_dict = json.loads(escalation.evidence)
        except Exception:
            evidence_dict = {"raw": escalation.evidence}

    return {
        "id": escalation.id,
        "hospital_id": escalation.hospital_id,
        "patient_id": escalation.patient_id,
        "queue_item_id": escalation.queue_item_id,
        "call_id": escalation.call_id,
        "consensus_assessment_id": escalation.consensus_assessment_id,
        "reason": escalation.reason,
        "priority": escalation.priority,
        "evidence": json.dumps(evidence_dict) if isinstance(evidence_dict, dict) else escalation.evidence,
        "status": escalation.status,
        "source": escalation.source,
        "final_action": escalation.final_action,
        "created_at": escalation.created_at,
        "updated_at": escalation.updated_at,
        "resolved_at": escalation.resolved_at,
        "resolution_notes": escalation.resolution_notes,
    }

