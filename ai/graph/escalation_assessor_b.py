import json

from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import settings
from ai.schemas.consensus import (
    EscalationAssessment,
    validate_assessment,
)
from ai.graph.red_flag_rules import enforce_red_flag_safety


def get_assessor_b_model():

    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    ).with_structured_output(EscalationAssessment)


def run_assessment_b(
    patient_context: dict,
    intake_data: dict,
    triage_result: dict,
    protocol: str | None = None
) -> EscalationAssessment:

    prompt = f"""
You are Independent Escalation Assessor B
in a post-discharge healthcare outreach system.

Perform an independent safety review of this case.

Your assessment must focus on:

1. Explicit red flags
2. Patient-reported symptoms
3. Relevant patient context
4. Existing clinical triage
5. Hospital protocol requirements
6. Whether additional clinical review is required

You are NOT the final escalation decision-maker.

SAFETY RULES:

- Do not diagnose.
- Do not prescribe.
- Do not recommend medication changes.
- Do not invent facts.
- Do not remove or ignore documented red flags.
- Do not override hospital protocol.
- Do not create database records.
- Use only the supplied evidence.
- When evidence is uncertain, preserve the uncertainty.
- A documented safety concern must remain visible in the assessment.

PATIENT CONTEXT:
{json.dumps(patient_context, default=str, indent=2)}

VOICE INTAKE:
{json.dumps(intake_data, default=str, indent=2)}

CLINICAL TRIAGE:
{json.dumps(triage_result, default=str, indent=2)}

HOSPITAL PROTOCOL:
{protocol or "No protocol provided"}

Return only a structured escalation assessment.
"""

    model = get_assessor_b_model()

    result = model.invoke(prompt)

    risk_level, recommended_action = enforce_red_flag_safety(
        result.risk_level,
        result.recommended_action,
        result.red_flags
    )

    result.risk_level = risk_level
    result.recommended_action = recommended_action

    return validate_assessment(result)
