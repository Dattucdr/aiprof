from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from auth.dependencies import get_current_user
from core.tenant import get_tenant_id
from models.user import User
from ai.tools.protocol_tools import get_hospital_protocol
from ai.tools.escalation_tools import create_ai_escalation
from ai.schemas.tool_schemas import CreateEscalationRequest
from ai.tools.ehr_tools import get_patient_ehr_summary
from ai.graph.tool_agent import build_agent
from models.call import Call
from backend.services.conversation_service import (
    append_transcript,
    get_call_transcript
)
from backend.services.triage_service import (
    get_triage_assessment,
    get_patient_triage_history,
    assessment_to_dict,
)
from backend.services.triage_pipeline import run_call_triage
from backend.services.escalation_assessment_service import (
    run_escalation_assessment_a,
    run_escalation_assessment_b,
)
from ai.graph.consensus import run_consensus
from ai.schemas.consensus import EscalationAssessment
from services.audit_service import (
    create_audit_log,
    generate_correlation_id,
)
from backend.services.consensus_service import (
    create_consensus_assessment,
    get_consensus_assessment,
    get_call_consensus,
    consensus_to_dict,
)

from ai.graph.patient_context import build_patient_context
from ai.graph.triage import perform_triage

from langchain_core.messages import HumanMessage
from pydantic import BaseModel


class AITestRequest(BaseModel):
    message: str


from ai.graph.voice_intake import (
    build_voice_intake_graph,
    build_voice_conversation_graph,
    create_voice_intake_state,
    transcript_to_messages
)
from ai.graph.intake_extraction import extract_voice_intake

from ai.tools.patient_tools import (
    get_patient_summary,
    get_latest_discharge,
    get_patient_medications,
    get_patient_conditions,
    get_patient_care_plans,
)

router = APIRouter(
    prefix="/ai-tools",
    tags=["AI Tools"]
)


@router.get("/patients/{patient_id}/summary")
def patient_summary(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return get_patient_summary(
            db,
            patient_id,
            hospital_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )


@router.get("/patients/{patient_id}/discharge")
def patient_discharge(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_latest_discharge(
        db,
        patient_id,
        hospital_id
    )


@router.get("/patients/{patient_id}/medications")
def patient_medications(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_patient_medications(
        db,
        patient_id,
        hospital_id
    )


@router.get("/patients/{patient_id}/conditions")
def patient_conditions(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_patient_conditions(
        db,
        patient_id,
        hospital_id
    )


@router.get("/patients/{patient_id}/care-plans")
def patient_care_plans(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_patient_care_plans(
        db,
        patient_id,
        hospital_id
    )

@router.get("/protocol")
def hospital_protocol(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_hospital_protocol(
        db,
        current_user.hospital_id
    )

@router.post("/escalations")
def create_escalation(
    request: CreateEscalationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_ai_escalation(
        db=db,
        hospital_id=current_user.hospital_id,
        patient_id=request.patient_id,
        queue_item_id=request.queue_item_id,
        reason=request.reason,
        priority=request.priority,
        evidence=request.evidence
    )


@router.get("/patients/{patient_id}/ehr")
def patient_ehr(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_patient_ehr_summary(
        db=db,
        hospital_id=current_user.hospital_id,
        patient_id=patient_id
    )

@router.post("/agent/test")
def test_ai_agent(
    request: AITestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = build_agent(
        db=db,
        hospital_id=current_user.hospital_id
    )

    result = agent.invoke({
        "messages": [
            HumanMessage(content=request.message)
        ]
    })

    return {
        "response": result["messages"][-1].content
    }


@router.post("/voice/test/{patient_id}/{call_id}/{queue_item_id}")
def test_voice_intake(
    patient_id: int,
    call_id: int,
    queue_item_id: int,
    current_user: User = Depends(get_current_user)
):
    graph = build_voice_intake_graph()

    state = create_voice_intake_state(
        patient_id=patient_id,
        call_id=call_id,
        queue_item_id=queue_item_id
    )

    result = graph.invoke(state)

    return result

class VoiceMessageRequest(BaseModel):
    patient_id: int
    call_id: int
    queue_item_id: int
    message: str

@router.post("/voice/conversation")
def voice_conversation(
    request: VoiceMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    call = (
        db.query(Call)
        .filter(
            Call.id == request.call_id,
            Call.hospital_id == current_user.hospital_id
        )
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found"
        )

    if call.patient_id != request.patient_id:
        raise HTTPException(
            status_code=400,
            detail="Patient does not belong to this call"
        )

    if call.queue_item_id != request.queue_item_id:
        raise HTTPException(
            status_code=400,
            detail="Queue item does not belong to this call"
        )

    if call.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="Conversation is allowed only for an active call"
        )

    transcript = get_call_transcript(
        db=db,
        call_id=request.call_id,
        hospital_id=current_user.hospital_id
    )

    graph = build_voice_conversation_graph()

    state = create_voice_intake_state(
        patient_id=request.patient_id,
        call_id=request.call_id,
        queue_item_id=request.queue_item_id
    )

    previous_messages = transcript_to_messages(
        transcript
    )

    state["messages"] = previous_messages

    state["messages"].append(
        HumanMessage(
            content=request.message
        )
    )

    result = graph.invoke(state)

    ai_response = result["messages"][-1].content

    append_transcript(
        db=db,
        call_id=request.call_id,
        hospital_id=current_user.hospital_id,
        speaker="Patient",
        message=request.message
    )

    append_transcript(
        db=db,
        call_id=request.call_id,
        hospital_id=current_user.hospital_id,
        speaker="Agent",
        message=ai_response
    )

    return {
        "patient_id": request.patient_id,
        "call_id": request.call_id,
        "response": ai_response,
        "transcript": get_call_transcript(
            db=db,
            call_id=request.call_id,
            hospital_id=current_user.hospital_id
        )
    }


@router.post("/voice/extract/{call_id}")
def extract_call_intake(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == current_user.hospital_id
        )
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found"
        )

    transcript = call.transcript or ""

    if not transcript.strip():
        raise HTTPException(
            status_code=400,
            detail="Call transcript is empty"
        )

    try:
        result = extract_voice_intake(transcript)

        return {
            "call_id": call.id,
            "patient_id": call.patient_id,
            "extraction": result.model_dump()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Intake extraction failed: {str(e)}"
        )

@router.post("/triage/test")
def test_triage(
    patient_context: str,
    intake_data: dict,
    protocol: str | None = None,
    current_user: User = Depends(get_current_user)
):
    try:

        result = perform_triage(
            patient_context=patient_context,
            intake_data=intake_data,
            protocol=protocol
        )

        return {
            "triage": result.model_dump()
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Triage failed: {str(e)}"
        )


@router.post("/triage/patient/{patient_id}")
def triage_patient(
    patient_id: int,
    intake_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        patient_context = build_patient_context(
            db=db,
            hospital_id=current_user.hospital_id,
            patient_id=patient_id
        )

        protocol_data = get_hospital_protocol(
            db=db,
            hospital_id=current_user.hospital_id
        )

        result = perform_triage(
            patient_context=patient_context,
            intake_data=intake_data,
            protocol=protocol_data.get("protocols")
        )

        return {
            "patient_id": patient_id,
            "triage": result.model_dump()
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Patient triage failed: {str(e)}"
        )


@router.get("/triage/assessments/{assessment_id}")
def get_triage(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        assessment = get_triage_assessment(
            db=db,
            hospital_id=current_user.hospital_id,
            assessment_id=assessment_id
        )

        return assessment_to_dict(assessment)

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get("/triage/patient/{patient_id}/history")
def get_patient_triage(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessments = get_patient_triage_history(
        db=db,
        hospital_id=current_user.hospital_id,
        patient_id=patient_id
    )

    return {
        "patient_id": patient_id,
        "count": len(assessments),
        "assessments": [
            assessment_to_dict(assessment)
            for assessment in assessments
        ]
    }


@router.post("/triage/call/{call_id}")
def triage_call(
    call_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        result = run_call_triage(
            db=db,
            hospital_id=current_user.hospital_id,
            call_id=call_id
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Call triage failed: {str(e)}"
        )


@router.post("/escalation/assessment-a/{patient_id}")
def escalation_assessment_a(
    patient_id: int,
    intake_data: dict,
    triage_result: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        result = run_escalation_assessment_a(
            db=db,
            hospital_id=current_user.hospital_id,
            patient_id=patient_id,
            intake_data=intake_data,
            triage_result=triage_result
        )

        return {
            "assessment": result.model_dump()
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Assessment A failed: {str(e)}"
        )


@router.post("/escalation/assessment-b/{patient_id}")
def escalation_assessment_b(
    patient_id: int,
    intake_data: dict,
    triage_result: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        result = run_escalation_assessment_b(
            db=db,
            hospital_id=current_user.hospital_id,
            patient_id=patient_id,
            intake_data=intake_data,
            triage_result=triage_result
        )

        return {
            "assessment": result.model_dump()
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Assessment B failed: {str(e)}"
        )


@router.post(
    "/escalation/consensus/{call_id}"
)
def create_call_consensus(
    call_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    hospital_id = current_user.hospital_id

    # ---------------------------------------------------------
    # Find call
    # ---------------------------------------------------------

    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == hospital_id,
        )
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    # ---------------------------------------------------------
    # Check existing consensus
    # ---------------------------------------------------------

    existing = get_call_consensus(
        db,
        hospital_id,
        call_id,
    )

    if existing:
        return {
            "existing": True,
            "consensus": consensus_to_dict(existing),
        }

    correlation_id = generate_correlation_id()

    # ---------------------------------------------------------
    # Get Assessment A
    # ---------------------------------------------------------

    assessment_a = run_escalation_assessment_a(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        intake_data={},
        triage_result={},
    )

    create_audit_log(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        action="ESCALATION_ASSESSMENT_A_COMPLETED",
        entity_type="ESCALATION_ASSESSMENT",
        correlation_id=correlation_id,
        details={
            "risk_level": assessment_a.risk_level,
            "recommended_action": assessment_a.recommended_action,
        },
    )

    # ---------------------------------------------------------
    # Get Assessment B
    # ---------------------------------------------------------

    assessment_b = run_escalation_assessment_b(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        intake_data={},
        triage_result={},
    )

    create_audit_log(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        action="ESCALATION_ASSESSMENT_B_COMPLETED",
        entity_type="ESCALATION_ASSESSMENT",
        correlation_id=correlation_id,
        details={
            "risk_level": assessment_b.risk_level,
            "recommended_action": assessment_b.recommended_action,
        },
    )

    # ---------------------------------------------------------
    # Deterministic consensus
    # ---------------------------------------------------------

    result = run_consensus(
        assessment_a,
        assessment_b,
    )

    # ---------------------------------------------------------
    # Persist
    # ---------------------------------------------------------

    consensus = create_consensus_assessment(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        queue_item_id=call.queue_item_id,
        result=result,
    )

    create_audit_log(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        action="CONSENSUS_COMPLETED",
        entity_type="CONSENSUS_ASSESSMENT",
        entity_id=consensus.id,
        correlation_id=correlation_id,
        details={
            "consensus_reached": result.consensus_reached,
            "disagreement": result.disagreement,
            "final_risk_level": result.final_risk_level,
            "final_action": result.final_action,
        },
    )


    return {
        "existing": False,
        "consensus": consensus_to_dict(consensus),
    }


@router.get("/consensus/call/{call_id}")
def read_call_consensus(
    call_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = get_call_consensus(
        db,
        current_user.hospital_id,
        call_id,
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Consensus assessment not found for this call",
        )

    return consensus_to_dict(existing)