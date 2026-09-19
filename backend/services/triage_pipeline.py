import json

from sqlalchemy.orm import Session

from models.call import Call

from ai.graph.intake_extraction import extract_voice_intake
from ai.graph.patient_context import build_patient_context
from ai.graph.triage import perform_triage
from ai.tools.protocol_tools import get_hospital_protocol

from services.audit_service import (
    create_audit_log,
    generate_correlation_id,
)

from backend.services.triage_service import (
    create_triage_assessment,
    get_call_triage_assessment,
)



def run_call_triage(
    db: Session,
    hospital_id: int,
    call_id: int
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == hospital_id
        )
        .first()
    )

    if not call:
        raise ValueError("Call not found")

    existing_assessment = get_call_triage_assessment(
        db=db,
        hospital_id=hospital_id,
        call_id=call_id
    )

    if existing_assessment:
        return {
            "call_id": call.id,
            "patient_id": call.patient_id,
            "intake": None,
            "triage": {
                "risk_level": existing_assessment.risk_level,
                "evidence": json.loads(
                    existing_assessment.evidence or "[]"
                ),
                "red_flags": json.loads(
                    existing_assessment.red_flags or "[]"
                ),
                "recommended_action":
                    existing_assessment.recommended_action,
                "confidence": existing_assessment.confidence
            },
            "assessment_id": existing_assessment.id,
            "existing": True
        }

    if not call.transcript or not call.transcript.strip():
        raise ValueError("Call transcript is empty")

    # -------------------------------------------------
    # 1. Extract structured intake from transcript
    # -------------------------------------------------

    intake_result = extract_voice_intake(
        call.transcript
    )

    intake_data = intake_result.model_dump()

    # -------------------------------------------------
    # 2. Build patient context
    # -------------------------------------------------

    patient_context = build_patient_context(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id
    )

    # -------------------------------------------------
    # 3. Load hospital protocol
    # -------------------------------------------------

    protocol_data = get_hospital_protocol(
        db=db,
        hospital_id=hospital_id
    )

    # -------------------------------------------------
    # 4. Perform clinical triage
    # -------------------------------------------------

    triage_result = perform_triage(
        patient_context=patient_context,
        intake_data=intake_data,
        protocol=protocol_data.get("protocols")
    )

    # -------------------------------------------------
    # 5. Persist triage assessment
    # -------------------------------------------------

    assessment = create_triage_assessment(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        queue_item_id=call.queue_item_id,
        triage_result=triage_result
    )

    create_audit_log(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        action="TRIAGE_COMPLETED",
        entity_type="TRIAGE_ASSESSMENT",
        entity_id=assessment.id,
        correlation_id=generate_correlation_id(),
        details={
            "risk_level": triage_result.risk_level,
            "recommended_action": triage_result.recommended_action,
        },
    )


    return {
        "call_id": call.id,
        "patient_id": call.patient_id,
        "intake": intake_data,
        "triage": triage_result.model_dump(),
        "assessment_id": assessment.id
    }
