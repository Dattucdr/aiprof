import json
from datetime import datetime

from sqlalchemy.orm import Session

from models.escalation import Escalation
from models.consensus_assessment import ConsensusAssessment
from services.audit_service import create_audit_log



ESCALATION_ACTIONS = {
    "CLINICAL_REVIEW",
    "URGENT_CLINICAL_REVIEW",
}


ALLOWED_ESCALATION_TRANSITIONS = {
    "OPEN": {
        "IN_REVIEW",
        "CLOSED",
    },

    "IN_REVIEW": {
        "RESOLVED",
        "CLOSED",
    },

    "RESOLVED": {
        "CLOSED",
    },

    "CLOSED": set(),
}


def should_create_escalation(final_action: str) -> bool:
    return final_action in ESCALATION_ACTIONS


def determine_escalation_priority(
    final_risk_level: str,
    final_action: str,
) -> str:

    if (
        final_risk_level == "CRITICAL"
        or final_action == "URGENT_CLINICAL_REVIEW"
    ):
        return "CRITICAL"

    if final_risk_level == "HIGH":
        return "HIGH"

    return "MEDIUM"


def create_escalation_from_consensus(
    db: Session,
    consensus: ConsensusAssessment,
):
    # ---------------------------------------------------------
    # 1. Check whether escalation is required
    # ---------------------------------------------------------

    if not should_create_escalation(
        consensus.final_action
    ):
        return None

    # ---------------------------------------------------------
    # 2. Idempotency check
    # ---------------------------------------------------------

    existing = (
        db.query(Escalation)
        .filter(
            Escalation.hospital_id == consensus.hospital_id,
            Escalation.consensus_assessment_id == consensus.id,
        )
        .first()
    )

    if existing:
        return existing

    # ---------------------------------------------------------
    # 3. Determine priority
    # ---------------------------------------------------------

    priority = determine_escalation_priority(
        consensus.final_risk_level,
        consensus.final_action,
    )

    # ---------------------------------------------------------
    # 4. Build reason
    # ---------------------------------------------------------

    reason = (
        f"Consensus decision requires "
        f"{consensus.final_action}. "
        f"Final risk level: "
        f"{consensus.final_risk_level}."
    )

    if consensus.disagreement:
        reason += (
            " Independent assessments disagreed."
        )

    # ---------------------------------------------------------
    # 5. Create escalation
    # ---------------------------------------------------------

    escalation = Escalation(
        hospital_id=consensus.hospital_id,
        patient_id=consensus.patient_id,
        queue_item_id=consensus.queue_item_id,

        call_id=consensus.call_id,

        consensus_assessment_id=consensus.id,

        reason=reason,

        priority=priority,

        evidence=json.dumps({
            "assessment_a": json.loads(
                consensus.assessment_a
            ),
            "assessment_b": json.loads(
                consensus.assessment_b
            ),
            "consensus_evidence": json.loads(
                consensus.evidence or "[]"
            ),
            "red_flags": json.loads(
                consensus.red_flags or "[]"
            ),
        }),

        status="OPEN",

        source="AI",

        final_action=consensus.final_action,

        created_at=datetime.utcnow(),
    )

    db.add(escalation)
    db.commit()
    db.refresh(escalation)

    create_audit_log(
        db=db,
        hospital_id=consensus.hospital_id,
        patient_id=consensus.patient_id,
        call_id=consensus.call_id,
        action="ESCALATION_CREATED",
        entity_type="ESCALATION",
        entity_id=escalation.id,
        details={
            "priority": escalation.priority,
            "final_action": escalation.final_action,
        },
    )

    return escalation



def get_escalation(
    db: Session,
    hospital_id: int,
    escalation_id: int,
):
    return (
        db.query(Escalation)
        .filter(
            Escalation.id == escalation_id,
            Escalation.hospital_id == hospital_id,
        )
        .first()
    )


def get_hospital_escalations(
    db: Session,
    hospital_id: int,
):
    return (
        db.query(Escalation)
        .filter(
            Escalation.hospital_id == hospital_id,
        )
        .order_by(
            Escalation.created_at.desc()
        )
        .all()
    )


def get_patient_escalations(
    db: Session,
    hospital_id: int,
    patient_id: int,
):
    return (
        db.query(Escalation)
        .filter(
            Escalation.hospital_id == hospital_id,
            Escalation.patient_id == patient_id,
        )
        .order_by(
            Escalation.created_at.desc()
        )
        .all()
    )



def update_escalation_status(
    db: Session,
    escalation: Escalation,
    new_status: str,
    resolution_notes: str | None = None,
):
    current_status = escalation.status

    allowed = ALLOWED_ESCALATION_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed:
        raise ValueError(
            f"Invalid escalation transition: "
            f"{current_status} -> {new_status}"
        )

    escalation.status = new_status

    if new_status in {
        "RESOLVED",
        "CLOSED",
    }:
        escalation.resolved_at = datetime.utcnow()

        if resolution_notes:
            escalation.resolution_notes = (
                resolution_notes
            )

    db.commit()
    db.refresh(escalation)

    return escalation
