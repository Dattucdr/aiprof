from pydantic import BaseModel, Field


class PatientSummaryRequest(BaseModel):
    patient_id: int = Field(..., description="Patient ID")


class LatestDischargeRequest(BaseModel):
    patient_id: int = Field(..., description="Patient ID")


class PatientMedicationsRequest(BaseModel):
    patient_id: int = Field(..., description="Patient ID")


class PatientConditionsRequest(BaseModel):
    patient_id: int = Field(..., description="Patient ID")


class PatientCarePlansRequest(BaseModel):
    patient_id: int = Field(..., description="Patient ID")

class CreateEscalationRequest(BaseModel):
    patient_id: int = Field(..., description="Patient ID")

    queue_item_id: int | None = Field(
        None,
        description="Related queue item ID"
    )

    reason: str = Field(
        ...,
        min_length=1,
        description="Reason for escalation"
    )

    priority: str = Field(
        ...,
        description="LOW, MEDIUM, HIGH, or CRITICAL"
    )

    evidence: str | None = Field(
        None,
        description="Evidence supporting the escalation"
    )