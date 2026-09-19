from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsensusAssessmentResponse(BaseModel):
    id: int

    hospital_id: int
    patient_id: int
    call_id: int
    queue_item_id: int | None

    assessment_a: dict
    assessment_b: dict

    consensus_reached: bool
    disagreement: bool
    disagreement_reason: str | None

    final_risk_level: str
    final_action: str

    evidence: list[str] = Field(
        default_factory=list
    )

    red_flags: list[str] = Field(
        default_factory=list
    )

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
