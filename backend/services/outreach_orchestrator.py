from sqlalchemy.orm import Session

from models.call import Call

from services.triage_service import (
    get_call_triage_assessment,
)

from services.triage_pipeline import (
    run_call_triage,
)

from services.escalation_assessment_service import (
    run_escalation_assessment_a,
    run_escalation_assessment_b,
)

from services.escalation_assessment_persistence import (
    save_assessment,
)

from ai.graph.consensus import run_consensus

from services.consensus_service import (
    create_consensus_assessment,
)

from services.escalation_service import (
    create_escalation_from_consensus,
)

from ai.graph.documentation import (
    generate_documentation,
)

from services.documentation_service import (
    create_documentation,
)

from workers.ehr_worker import (
    write_documentation_to_ehr,
)

from services.audit_service import (
    create_audit_log,
    generate_correlation_id,
)


def run_outreach_orchestration(
    db: Session,
    hospital_id: int,
    call_id: int,
):
    correlation_id = generate_correlation_id()

    # ---------------------------------------------------------
    # 1. Find call
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
        raise ValueError("Call not found")

    if not call.transcript:
        raise ValueError(
            "Call transcript is empty"
        )

    # ---------------------------------------------------------
    # 2. Run / retrieve triage
    # ---------------------------------------------------------

    triage_result = run_call_triage(
        db=db,
        hospital_id=hospital_id,
        call_id=call_id,
    )

    intake_data = triage_result["intake"]

    triage_data = triage_result["triage"]

    triage_assessment_id = (
        triage_result["assessment_id"]
    )

    create_audit_log(
        db=db,
        action="TRIAGE_COMPLETED",
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        entity_type="triage_assessment",
        entity_id=triage_assessment_id,
        correlation_id=correlation_id,
    )

    # ---------------------------------------------------------
    # 3. Run Assessment A
    # ---------------------------------------------------------

    assessment_a = (
        run_escalation_assessment_a(
            db=db,
            hospital_id=hospital_id,
            patient_id=call.patient_id,
            intake_data=intake_data,
            triage_result=triage_data,
        )
    )

    assessment_a_record = save_assessment(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        queue_item_id=call.queue_item_id,
        assessment=assessment_a,
    )

    create_audit_log(
        db=db,
        action="ESCALATION_ASSESSMENT_A_COMPLETED",
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        entity_type="escalation_assessment",
        entity_id=assessment_a_record.id,
        correlation_id=correlation_id,
    )

    # ---------------------------------------------------------
    # 4. Run Assessment B
    # ---------------------------------------------------------

    assessment_b = (
        run_escalation_assessment_b(
            db=db,
            hospital_id=hospital_id,
            patient_id=call.patient_id,
            intake_data=intake_data,
            triage_result=triage_data,
        )
    )

    assessment_b_record = save_assessment(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        queue_item_id=call.queue_item_id,
        assessment=assessment_b,
    )

    create_audit_log(
        db=db,
        action="ESCALATION_ASSESSMENT_B_COMPLETED",
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        entity_type="escalation_assessment",
        entity_id=assessment_b_record.id,
        correlation_id=correlation_id,
    )

    # ---------------------------------------------------------
    # 5. Deterministic consensus
    # ---------------------------------------------------------

    consensus_result = run_consensus(
        assessment_a,
        assessment_b,
    )

    # ---------------------------------------------------------
    # 6. Persist consensus
    # ---------------------------------------------------------

    consensus = create_consensus_assessment(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        queue_item_id=call.queue_item_id,
        result=consensus_result,
    )

    create_audit_log(
        db=db,
        action="CONSENSUS_COMPLETED",
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        entity_type="consensus_assessment",
        entity_id=consensus.id,
        correlation_id=correlation_id,
        details={
            "final_risk_level": (
                consensus.final_risk_level
            ),
            "final_action": (
                consensus.final_action
            ),
            "disagreement": (
                consensus.disagreement
            ),
        },
    )

    # ---------------------------------------------------------
    # 7. Create escalation if required
    # ---------------------------------------------------------

    escalation = (
        create_escalation_from_consensus(
            db=db,
            consensus=consensus,
        )
    )

    if escalation:
        create_audit_log(
            db=db,
            action="ESCALATION_CREATED",
            hospital_id=hospital_id,
            patient_id=call.patient_id,
            call_id=call.id,
            entity_type="escalation",
            entity_id=escalation.id,
            correlation_id=correlation_id,
            details={
                "priority": escalation.priority,
                "final_action": (
                    escalation.final_action
                ),
            },
        )

    # ---------------------------------------------------------
    # 8. Prepare escalation data
    # ---------------------------------------------------------

    escalation_data = None

    if escalation:
        escalation_data = {
            "id": escalation.id,
            "status": escalation.status,
            "priority": escalation.priority,
            "reason": escalation.reason,
            "final_action": escalation.final_action,
        }

    # ---------------------------------------------------------
    # 9. Generate documentation
    # ---------------------------------------------------------

    documentation_result = (
        generate_documentation(
            transcript=call.transcript,
            intake_data=intake_data,
            triage_result=triage_data,
            consensus_result=consensus_result.model_dump(),
            escalation_data=escalation_data,
        )
    )

    # ---------------------------------------------------------
    # 10. Persist documentation
    # ---------------------------------------------------------

    documentation = create_documentation(
        db=db,
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        triage_assessment_id=triage_assessment_id,
        consensus_assessment_id=consensus.id,
        escalation_id=(
            escalation.id
            if escalation
            else None
        ),
        documentation=documentation_result,
    )

    create_audit_log(
        db=db,
        action="DOCUMENTATION_CREATED",
        hospital_id=hospital_id,
        patient_id=call.patient_id,
        call_id=call.id,
        entity_type="outreach_documentation",
        entity_id=documentation.id,
        correlation_id=correlation_id,
    )

    # ---------------------------------------------------------
    # 11. Schedule EHR write
    # ---------------------------------------------------------

    ehr_task = (
        write_documentation_to_ehr.delay(
            documentation.id
        )
    )

    return {
        "call_id": call.id,
        "triage_assessment_id": triage_assessment_id,
        "consensus_assessment_id": consensus.id,
        "escalation_id": (
            escalation.id
            if escalation
            else None
        ),
        "documentation_id": documentation.id,
        "ehr_task_id": ehr_task.id,
        "correlation_id": correlation_id,
    }
