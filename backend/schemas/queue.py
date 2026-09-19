from datetime import datetime
from pydantic import BaseModel


class QueueStatusUpdate(BaseModel):
    status: str


class QueueDispatchResponse(BaseModel):
    reserved: bool
    queue_item_id: int | None = None
    patient_id: int | None = None
    campaign_id: int | None = None
    status: str | None = None
    worker_id: str | None = None
    priority_score: float | None = None
    attempt_count: int | None = None
    locked_at: datetime | None = None
    reason: str | None = None
    
class CallOutcomeRequest(BaseModel):
    outcome: str


class CallbackRequest(BaseModel):
    callback_at: datetime