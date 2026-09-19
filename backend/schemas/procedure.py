from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProcedureCreate(BaseModel):
    procedure_name: str
    status: str = "COMPLETED"
    performed_at: datetime | None = None
    description: str | None = None
    notes: str | None = None


class ProcedureResponse(ProcedureCreate):
    id: int
    patient_id: int
    hospital_id: int
    encounter_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
