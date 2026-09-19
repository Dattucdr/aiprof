from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CallCreate(BaseModel):
    queue_item_id: int
    worker_id: str
    idempotency_key: str


class CallOutcomeRequest(BaseModel):
    outcome: str
    notes: str | None = None
    transcript: str | None = None


class CallResponse(BaseModel):
    id: int
    hospital_id: int
    campaign_id: int
    patient_id: int
    queue_item_id: int
    attempt_number: int
    idempotency_key: str
    status: str
    outcome: str | None
    worker_id: str | None
    started_at: datetime | None
    connected_at: datetime | None
    ended_at: datetime | None
    duration_seconds: int | None
    transcript: str | None
    notes: str | None
    failure_reason: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
