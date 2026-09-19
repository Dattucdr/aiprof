from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    name: str
    description: str | None = None
    priority: int = 5
    follow_up_window_days: int = 7
    max_retry_attempts: int | None = None
    rules: str | None = None
    calling_start_time: str | None = None
    calling_end_time: str | None = None
    scheduled_at: datetime | None = None


class CampaignResponse(CampaignCreate):
    id: int
    hospital_id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignStatusUpdate(BaseModel):
    status: str


class CampaignPreviewResponse(BaseModel):
    campaign_id: int
    campaign_name: str
    campaign_status: str
    total_patients_evaluated: int
    eligible_count: int
    ineligible_count: int
    eligible_patient_ids: list[int]


