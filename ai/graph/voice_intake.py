from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings


def transcript_to_messages(transcript: str):
    messages = []

    if not transcript:
        return messages

    for line in transcript.splitlines():

        if "Agent:" in line:
            content = line.split("Agent:", 1)[1].strip()

            messages.append(
                {
                    "role": "assistant",
                    "content": content
                }
            )

        elif "Patient:" in line:
            content = line.split("Patient:", 1)[1].strip()

            messages.append(
                {
                    "role": "user",
                    "content": content
                }
            )

    return messages



class VoiceIntakeState(TypedDict):
    patient_id: int
    call_id: int
    queue_item_id: int

    messages: Annotated[list[BaseMessage], add_messages]

    current_step: str

    symptoms: list[str]
    red_flags: list[str]

    medication_concerns: list[str]

    patient_questions: list[str]

    consent_confirmed: bool
    identity_verified: bool

    conversation_completed: bool


def create_voice_intake_state(
    patient_id: int,
    call_id: int,
    queue_item_id: int
):
    return {
        "patient_id": patient_id,
        "call_id": call_id,
        "queue_item_id": queue_item_id,

        "messages": [],

        "current_step": "INTRODUCTION",

        "symptoms": [],
        "red_flags": [],

        "medication_concerns": [],

        "patient_questions": [],

        "consent_confirmed": False,
        "identity_verified": False,

        "conversation_completed": False,
    }


def introduction_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "INTRODUCTION"}


def verify_patient_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "VERIFY_PATIENT"}


def wellbeing_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "WELLBEING"}


def symptoms_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "SYMPTOMS"}


def red_flag_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "RED_FLAGS"}


def medication_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "MEDICATION"}


def patient_questions_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "PATIENT_QUESTIONS"}


def complete_node(state: VoiceIntakeState) -> dict:
    return {"current_step": "COMPLETE", "conversation_completed": True}


def build_voice_intake_graph():

    graph = StateGraph(VoiceIntakeState)

    graph.add_node(
        "introduction",
        introduction_node
    )

    graph.add_node(
        "verify_patient",
        verify_patient_node
    )

    graph.add_node(
        "wellbeing",
        wellbeing_node
    )

    graph.add_node(
        "symptoms",
        symptoms_node
    )

    graph.add_node(
        "red_flags",
        red_flag_node
    )

    graph.add_node(
        "medication",
        medication_node
    )

    graph.add_node(
        "patient_questions",
        patient_questions_node
    )

    graph.add_node(
        "complete",
        complete_node
    )

    graph.add_edge(
        START,
        "introduction"
    )

    graph.add_edge(
        "introduction",
        "verify_patient"
    )

    graph.add_edge(
        "verify_patient",
        "wellbeing"
    )

    graph.add_edge(
        "wellbeing",
        "symptoms"
    )

    graph.add_edge(
        "symptoms",
        "red_flags"
    )

    graph.add_edge(
        "red_flags",
        "medication"
    )

    graph.add_edge(
        "medication",
        "patient_questions"
    )

    graph.add_edge(
        "patient_questions",
        "complete"
    )

    graph.add_edge(
        "complete",
        END
    )

    return graph.compile()


def get_voice_model():

    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    )


def conversation_node(state: VoiceIntakeState):

    model = get_voice_model()

    system_prompt = """
You are a healthcare post-discharge outreach assistant.

Your role is to conduct a structured follow-up conversation.

You must:
- Be polite and concise.
- Ask one question at a time.
- Never diagnose.
- Never prescribe.
- Never change medications.
- Never provide treatment instructions outside approved protocols.
- If the patient reports potentially serious symptoms, flag them
  for clinical review rather than making a clinical decision.
- Do not invent patient information.

Current conversation step:
{step}

Known symptoms:
{symptoms}

Known medication concerns:
{medication_concerns}

Known patient questions:
{patient_questions}
"""

    prompt = system_prompt.format(
        step=state["current_step"],
        symptoms=state["symptoms"],
        medication_concerns=state["medication_concerns"],
        patient_questions=state["patient_questions"]
    )

    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]

    messages.extend(state["messages"])

    response = model.invoke(messages)

    return {
        "messages": [response]
    }

def add_patient_response(
    state: VoiceIntakeState,
    response: str
):
    return {
        "messages": [
            {
                "role": "user",
                "content": response
            }
        ]
    }

def build_voice_conversation_graph():

    graph = StateGraph(VoiceIntakeState)

    graph.add_node(
        "conversation",
        conversation_node
    )

    graph.add_edge(
        START,
        "conversation"
    )

    graph.add_edge(
        "conversation",
        END
    )

    return graph.compile()