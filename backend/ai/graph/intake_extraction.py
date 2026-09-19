from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings
from ai.schemas.voice_intake import VoiceIntakeExtraction

def get_intake_extraction_model():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    ).with_structured_output(VoiceIntakeExtraction)

def extract_voice_intake(transcript: str) -> VoiceIntakeExtraction:
    prompt = f"""
You are a healthcare post-discharge voice intake extraction system.

Your job is ONLY to extract information explicitly stated by the patient
from the conversation.

Do NOT:
- diagnose the patient
- recommend treatment
- recommend medications
- invent symptoms
- infer medical conditions
- make an escalation decision
- assign clinical priority

Extract only information supported by the conversation.

Conversation:
{transcript}
"""
    model = get_intake_extraction_model()
    return model.invoke(prompt)
