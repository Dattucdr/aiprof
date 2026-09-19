from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class PatientCreate(BaseModel):
    medical_record_number: str
    first_name: str
    last_name: str
    date_of_birth: datetime | None = None
    gender: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    communication_consent: bool = True
    preferred_language: str = "English"
    preferred_call_time: str | None = None


class PatientResponse(PatientCreate):
    id: int
    hospital_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
