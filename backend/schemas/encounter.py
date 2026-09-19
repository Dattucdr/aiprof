from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EncounterCreate(BaseModel):
    encounter_type: str
    admission_datetime: datetime
    discharge_datetime: datetime | None = None
    discharge_status: str | None = None
    reason: str | None = None
    discharge_instructions: str | None = None


class EncounterResponse(EncounterCreate):
    id: int
    patient_id: int
    hospital_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
