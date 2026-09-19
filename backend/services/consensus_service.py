import json

from sqlalchemy.orm import Session

from models.consensus_assessment import ConsensusAssessment
from ai.schemas.consensus import ConsensusResult


def create_consensus_assessment(
    db: Session,
    hospital_id: int,
    patient_id: int,
    call_id: int,
    queue_item_id: int | None,
    result: ConsensusResult,
):
    existing = (
        db.query(ConsensusAssessment)
        .filter(
            ConsensusAssessment.hospital_id == hospital_id,
            ConsensusAssessment.call_id == call_id,
        )
        .first()
    )

    if existing:
        return existing

    assessment_a = result.assessments[0]
    assessment_b = result.assessments[1]

    assessment_a_data = assessment_a.model_dump()
    assessment_b_data = assessment_b.model_dump()

    consensus = ConsensusAssessment(
        hospital_id=hospital_id,
        patient_id=patient_id,
        call_id=call_id,
        queue_item_id=queue_item_id,

        assessment_a=json.dumps(
            assessment_a_data
        ),

        assessment_b=json.dumps(
            assessment_b_data
        ),

        consensus_reached=result.consensus_reached,
        disagreement=result.disagreement,
        disagreement_reason=result.disagreement_reason,

        final_risk_level=result.final_risk_level,
        final_action=result.final_action,

        evidence=json.dumps(
            result.evidence
        ),

        red_flags=json.dumps(
            result.red_flags
        ),
    )

    db.add(consensus)
    db.commit()
    db.refresh(consensus)

    return consensus


def consensus_to_dict(consensus):
    return {
        "id": consensus.id,
        "hospital_id": consensus.hospital_id,
        "patient_id": consensus.patient_id,
        "call_id": consensus.call_id,
        "queue_item_id": consensus.queue_item_id,

        "assessment_a": json.loads(
            consensus.assessment_a
        ),

        "assessment_b": json.loads(
            consensus.assessment_b
        ),

        "consensus_reached": consensus.consensus_reached,
        "disagreement": consensus.disagreement,
        "disagreement_reason": consensus.disagreement_reason,

        "final_risk_level": consensus.final_risk_level,
        "final_action": consensus.final_action,

        "evidence": json.loads(
            consensus.evidence or "[]"
        ),

        "red_flags": json.loads(
            consensus.red_flags or "[]"
        ),

        "created_at": consensus.created_at,
    }


def get_consensus_assessment(
    db: Session,
    hospital_id: int,
    assessment_id: int,
):
    return (
        db.query(ConsensusAssessment)
        .filter(
            ConsensusAssessment.id == assessment_id,
            ConsensusAssessment.hospital_id == hospital_id,
        )
        .first()
    )


def get_call_consensus(
    db: Session,
    hospital_id: int,
    call_id: int,
):
    return (
        db.query(ConsensusAssessment)
        .filter(
            ConsensusAssessment.hospital_id == hospital_id,
            ConsensusAssessment.call_id == call_id,
        )
        .first()
    )
