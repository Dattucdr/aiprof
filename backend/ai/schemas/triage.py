from pydantic import BaseModel, Field

class TriageResult(BaseModel):
    risk_level: str
    evidence: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    recommended_action: str
    confidence: float = Field(ge=0.0, le=1.0)
