from sqlalchemy.orm import Session

from models.patient import Patient
from models.encounter import Encounter
from models.observation import Observation
from ai.tools.validators import (
    validate_patient_id,
    validate_hospital_id
)

def get_patient_ehr_summary(
    db: Session,
    hospital_id: int,
    patient_id: int
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.hospital_id == hospital_id
        )
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    encounters = (
        db.query(Encounter)
        .filter(
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id
        )
        .order_by(Encounter.admission_datetime.desc())
        .all()
    )

    observations = (
        db.query(Observation)
        .filter(
            Observation.patient_id == patient_id,
            Observation.hospital_id == hospital_id
        )
        .order_by(Observation.observed_at.desc())
        .all()
    )

    return {
        "patient": {
            "id": patient.id,
            "medical_record_number": patient.medical_record_number,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
        },
        "encounters": [
            {
                "id": encounter.id,
                "encounter_type": encounter.encounter_type,
                "admission_datetime": encounter.admission_datetime,
                "discharge_datetime": encounter.discharge_datetime,
                "discharge_status": encounter.discharge_status,
                "reason": encounter.reason,
            }
            for encounter in encounters
        ],
        "observations": [
            {
                "id": observation.id,
                "code": observation.code,
                "value": observation.value,
                "unit": observation.unit,
                "observed_at": observation.observed_at,
            }
            for observation in observations
        ],
    }
