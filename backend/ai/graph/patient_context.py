from sqlalchemy.orm import Session

from ai.tools.patient_tools import (
    get_patient_summary,
    get_latest_discharge,
    get_patient_medications,
    get_patient_conditions,
    get_patient_care_plans,
)

def build_patient_context(
    db: Session,
    hospital_id: int,
    patient_id: int
) -> dict:
    return {
        "patient_summary": get_patient_summary(db, patient_id, hospital_id),
        "latest_discharge": get_latest_discharge(db, patient_id, hospital_id),
        "medications": get_patient_medications(db, patient_id, hospital_id),
        "conditions": get_patient_conditions(db, patient_id, hospital_id),
        "care_plans": get_patient_care_plans(db, patient_id, hospital_id),
    }
