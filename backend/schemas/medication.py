from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicationCreate(BaseModel):
    medication_name: str
    dosage: str | None = None
    route: str | None = None
    frequency: str | None = None
    instructions: str | None = None
    is_active: bool = True
    start_date: datetime | None = None
    end_date: datetime | None = None


class MedicationResponse(MedicationCreate):
    id: int
    patient_id: int
    hospital_id: int
    encounter_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
