import json
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings
from ai.schemas.documentation import OutreachDocumentation

def get_documentation_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY,
    ).with_structured_output(OutreachDocumentation)

def generate_documentation(
    transcript: str,
    intake_data: dict,
    triage_result: dict,
    consensus_result: dict,
    escalation_data: dict | None = None,
):
    model = get_documentation_model()
    prompt = f"""
You are a healthcare outreach documentation assistant.
Create a factual post-discharge outreach note.

PATIENT OUTREACH TRANSCRIPT:
{transcript}

INTAKE DATA:
{json.dumps(intake_data)}

TRIAGE RESULT:
{json.dumps(triage_result)}

CONSENSUS RESULT:
{json.dumps(consensus_result)}

ESCALATION:
{json.dumps(escalation_data)}

Create a concise structured documentation record.
"""
    result = model.invoke(prompt)
    return result
