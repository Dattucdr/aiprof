from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CarePlanCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "ACTIVE"
    goals: str | None = None
    follow_up_instructions: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class CarePlanResponse(CarePlanCreate):
    id: int
    patient_id: int
    hospital_id: int
    encounter_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
