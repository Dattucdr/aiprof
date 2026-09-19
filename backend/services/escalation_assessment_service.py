from sqlalchemy.orm import Session

from ai.graph.escalation_assessor_a import run_assessment_a
from ai.graph.escalation_assessor_b import run_assessment_b
from ai.graph.patient_context import build_patient_context
from ai.tools.protocol_tools import get_hospital_protocol
from ai.schemas.triage import TriageResult


def run_escalation_assessment_a(
    db: Session,
    hospital_id: int,
    patient_id: int,
    intake_data: dict,
    triage_result: dict
):

    patient_context = build_patient_context(
        db=db,
        hospital_id=hospital_id,
        patient_id=patient_id
    )

    protocol_data = get_hospital_protocol(
        db=db,
        hospital_id=hospital_id
    )

    assessment = run_assessment_a(
        patient_context=patient_context,
        intake_data=intake_data,
        triage_result=triage_result,
        protocol=protocol_data.get("protocols")
    )

    return assessment


def run_escalation_assessment_b(
    db: Session,
    hospital_id: int,
    patient_id: int,
    intake_data: dict,
    triage_result: dict
):

    patient_context = build_patient_context(
        db=db,
        hospital_id=hospital_id,
        patient_id=patient_id
    )

    protocol_data = get_hospital_protocol(
        db=db,
        hospital_id=hospital_id
    )

    assessment = run_assessment_b(
        patient_context=patient_context,
        intake_data=intake_data,
        triage_result=triage_result,
        protocol=protocol_data.get("protocols")
    )

    return assessment
