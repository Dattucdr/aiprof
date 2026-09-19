import json

from ai.schemas.triage import TriageResult
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings
from ai.graph.red_flag_rules import (
    detect_red_flags,
    enforce_red_flag_safety
)

ALLOWED_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
ALLOWED_ACTIONS = {"NO_ACTION", "FOLLOW_UP", "CLINICAL_REVIEW", "URGENT_CLINICAL_REVIEW"}

def validate_triage_result(result: TriageResult) -> TriageResult:
    if result.risk_level not in ALLOWED_RISK_LEVELS:
        raise ValueError(f"Invalid risk level: {result.risk_level}")
    if result.recommended_action not in ALLOWED_ACTIONS:
        raise ValueError(f"Invalid recommended action: {result.recommended_action}")

    risk_level, recommended_action = enforce_red_flag_safety(
        result.risk_level,
        result.recommended_action,
        result.red_flags
    )
    result.risk_level = risk_level
    result.recommended_action = recommended_action
    return result

def get_triage_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    ).with_structured_output(TriageResult)

def perform_triage(
    patient_context: dict,
    intake_data: dict,
    protocol: str | None = None
) -> TriageResult:
    transcript_text = str(intake_data)
    rule_based_flags = detect_red_flags(transcript_text)
    existing_flags = intake_data.get("red_flags", [])

    all_red_flags = list(existing_flags)
    for flag in rule_based_flags:
        if flag not in all_red_flags:
            all_red_flags.append(flag)

    intake_data = {
        **intake_data,
        "red_flags": all_red_flags
    }

    prompt = f"""
You are a clinical triage support component in a post-discharge healthcare outreach system.
Assess only the information provided below.

SAFETY RULES:
- Do not diagnose.
- Do not prescribe medication.
- Do not change medication.
- Do not invent patient information.
- Do not override hospital protocols.
- Do not suppress documented red flags.
- Use only supplied evidence.

PATIENT CONTEXT:
{json.dumps(patient_context, default=str, indent=2)}

VOICE INTAKE:
{json.dumps(intake_data, default=str, indent=2)}

HOSPITAL PROTOCOL:
{protocol or "No protocol provided"}

Return a structured triage assessment.
"""
    model = get_triage_model()
    result = model.invoke(prompt)
    return validate_triage_result(result)
