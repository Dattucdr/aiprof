from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EscalationStatusUpdate(BaseModel):
    status: str
    resolution_notes: str | None = None


class EscalationResponse(BaseModel):
    id: int

    hospital_id: int
    patient_id: int

    queue_item_id: int | None
    call_id: int | None
    consensus_assessment_id: int | None

    reason: str
    priority: str
    evidence: dict | None

    status: str
    source: str

    final_action: str | None

    created_at: datetime
    updated_at: datetime | None

    resolved_at: datetime | None
    resolution_notes: str | None

    model_config = ConfigDict(
        from_attributes=True
    )
