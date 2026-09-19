from pydantic import BaseModel, Field


class OutreachDocumentation(BaseModel):
    summary: str

    symptoms: list[str] = Field(
        default_factory=list
    )

    medication_concerns: list[str] = Field(
        default_factory=list
    )

    patient_questions: list[str] = Field(
        default_factory=list
    )

    red_flags: list[str] = Field(
        default_factory=list
    )

    triage_risk_level: str

    recommended_action: str

    escalation_created: bool

    escalation_reason: str | None = None

    follow_up_required: bool = False

    follow_up_notes: str | None = None
