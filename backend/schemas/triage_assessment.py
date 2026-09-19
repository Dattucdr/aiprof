from datetime import datetime

from pydantic import BaseModel, ConfigDict

class TriageAssessmentResponse(BaseModel):
    id: int
    hospital_id: int
    patient_id: int
    call_id: int | None
    queue_item_id: int | None
    risk_level: str
    recommended_action: str
    evidence: list[str]
    red_flags: list[str]
    confidence: float
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
