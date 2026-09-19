from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages

from ai.tools.patient_tools import (
    get_patient_summary,
    get_latest_discharge,
    get_patient_medications,
    get_patient_conditions,
    get_patient_care_plans,
)
from ai.tools.protocol_tools import get_hospital_protocol


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_patient_tools(db, hospital_id):

    def patient_summary(patient_id: int):
        return get_patient_summary(
            db=db,
            patient_id=patient_id,
            hospital_id=hospital_id
        )

    def latest_discharge(patient_id: int):
        return get_latest_discharge(
            db=db,
            patient_id=patient_id,
            hospital_id=hospital_id
        )

    def patient_medications(patient_id: int):
        return get_patient_medications(
            db=db,
            patient_id=patient_id,
            hospital_id=hospital_id
        )

    def patient_conditions(patient_id: int):
        return get_patient_conditions(
            db=db,
            patient_id=patient_id,
            hospital_id=hospital_id
        )

    def patient_care_plans(patient_id: int):
        return get_patient_care_plans(
            db=db,
            patient_id=patient_id,
            hospital_id=hospital_id
        )

    return [
        patient_summary,
        latest_discharge,
        patient_medications,
        patient_conditions,
        patient_care_plans,
    ]


def build_protocol_tool(db, hospital_id):

    def hospital_protocol():
        return get_hospital_protocol(
            db=db,
            hospital_id=hospital_id
        )

    return hospital_protocol


def build_agent(db, hospital_id):

    tools = build_patient_tools(
        db=db,
        hospital_id=hospital_id
    )

    tools.append(
        build_protocol_tool(
            db=db,
            hospital_id=hospital_id
        )
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0
    )

    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: AgentState):
        response = llm_with_tools.invoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }

    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)

    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        tools_condition
    )

    graph.add_edge("tools", "agent")

    return graph.compile()
