import json

from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import settings
from ai.schemas.consensus import (
    EscalationAssessment,
    validate_assessment,
)
from ai.graph.red_flag_rules import enforce_red_flag_safety


def get_assessor_a_model():

    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    ).with_structured_output(EscalationAssessment)


def run_assessment_a(
    patient_context: dict,
    intake_data: dict,
    triage_result: dict,
    protocol: str | None = None
) -> EscalationAssessment:

    prompt = f"""
You are Independent Escalation Assessor A
in a post-discharge healthcare outreach system.

Assess whether the case requires further clinical review.

You are NOT the final escalation decision-maker.

SAFETY RULES:

- Do not diagnose.
- Do not prescribe.
- Do not recommend medication changes.
- Do not invent patient information.
- Use only the supplied evidence.
- Preserve all documented red flags.
- Do not suppress a safety concern.
- Follow the supplied hospital protocol.
- If evidence is insufficient or uncertain, represent that uncertainty.
- Do not create or modify database records.

PATIENT CONTEXT:
{json.dumps(patient_context, default=str, indent=2)}

VOICE INTAKE:
{json.dumps(intake_data, default=str, indent=2)}

CLINICAL TRIAGE:
{json.dumps(triage_result, default=str, indent=2)}

HOSPITAL PROTOCOL:
{protocol or "No protocol provided"}

Return a structured escalation assessment.
"""

    model = get_assessor_a_model()

    result = model.invoke(prompt)

    risk_level, recommended_action = enforce_red_flag_safety(
        result.risk_level,
        result.recommended_action,
        result.red_flags
    )

    result.risk_level = risk_level
    result.recommended_action = recommended_action

    return validate_assessment(result)
