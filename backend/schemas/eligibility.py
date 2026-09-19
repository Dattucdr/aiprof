from pydantic import BaseModel


class EligibilityRules(BaseModel):
    min_days_after_discharge: int = 0
    max_days_after_discharge: int = 7
    require_consent: bool = True
    require_phone_number: bool = True
    require_discharge: bool = True
    allow_multiple_outreach: bool = False


class EligibilityResult(BaseModel):
    patient_id: int
    eligible: bool
    reasons: list[str]
