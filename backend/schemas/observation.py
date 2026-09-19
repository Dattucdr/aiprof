from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ObservationCreate(BaseModel):
    observation_type: str
    value: str
    unit: str | None = None
    status: str = "FINAL"
    notes: str | None = None
    observed_at: datetime


class ObservationResponse(ObservationCreate):
    id: int
    patient_id: int
    hospital_id: int
    encounter_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
