from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConditionCreate(BaseModel):
    condition_name: str
    clinical_status: str = "ACTIVE"
    severity: str | None = None
    description: str | None = None
    onset_date: datetime | None = None
    resolved_date: datetime | None = None


class ConditionResponse(ConditionCreate):
    id: int
    patient_id: int
    hospital_id: int
    encounter_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
