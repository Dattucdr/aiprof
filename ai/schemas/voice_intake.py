from pydantic import BaseModel, Field


class VoiceIntakeExtraction(BaseModel):
    symptoms: list[str] = Field(default_factory=list)

    red_flags: list[str] = Field(default_factory=list)

    medication_concerns: list[str] = Field(default_factory=list)

    patient_questions: list[str] = Field(default_factory=list)

    consent_confirmed: bool = False

    identity_verified: bool = False
