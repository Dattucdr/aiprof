from datetime import datetime
from pydantic import BaseModel


class DischargeResponse(BaseModel):
    patient_id: int
    encounter_id: int
    admission_datetime: datetime
    discharge_datetime: datetime
    discharge_status: str | None
    discharge_instructions: str | None
