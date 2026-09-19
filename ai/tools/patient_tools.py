from sqlalchemy.orm import Session

from models.patient import Patient
from models.encounter import Encounter
from models.medication import Medication
from models.condition import Condition
from models.care_plan import CarePlan
from ai.tools.validators import (
    validate_patient_id,
    validate_hospital_id
)


def get_patient_summary(
    db: Session,
    patient_id: int,
    hospital_id: int
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.hospital_id == hospital_id,
            Patient.active == True
        )
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    return {
        "patient_id": patient.id,
        "medical_record_number": patient.medical_record_number,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "phone_number": patient.phone_number,
        "preferred_language": patient.preferred_language,
        "preferred_call_time": patient.preferred_call_time,
        "communication_consent": patient.communication_consent,
    }


def get_latest_discharge(
    db: Session,
    patient_id: int,
    hospital_id: int
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)

    encounter = (
        db.query(Encounter)
        .filter(
            Encounter.patient_id == patient_id,
            Encounter.hospital_id == hospital_id,
            Encounter.discharge_status == "DISCHARGED"
        )
        .order_by(Encounter.discharge_datetime.desc())
        .first()
    )

    if not encounter:
        return None

    return {
        "encounter_id": encounter.id,
        "admission_datetime": encounter.admission_datetime,
        "discharge_datetime": encounter.discharge_datetime,
        "discharge_status": encounter.discharge_status,
        "reason": encounter.reason,
        "discharge_instructions": encounter.discharge_instructions,
    }


def get_patient_medications(
    db: Session,
    patient_id: int,
    hospital_id: int
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)

    medications = (
        db.query(Medication)
        .filter(
            Medication.patient_id == patient_id,
            Medication.hospital_id == hospital_id
        )
        .all()
    )

    return [
        {
            "id": medication.id,
            "name": medication.name,
            "dosage": medication.dosage,
            "frequency": medication.frequency,
            "route": medication.route,
            "status": medication.status,
        }
        for medication in medications
    ]


def get_patient_conditions(
    db: Session,
    patient_id: int,
    hospital_id: int
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)

    conditions = (
        db.query(Condition)
        .filter(
            Condition.patient_id == patient_id,
            Condition.hospital_id == hospital_id
        )
        .all()
    )

    return [
        {
            "id": condition.id,
            "name": condition.name,
            "status": condition.status,
            "severity": condition.severity,
        }
        for condition in conditions
    ]


def get_patient_care_plans(
    db: Session,
    patient_id: int,
    hospital_id: int
):
    validate_patient_id(patient_id)
    validate_hospital_id(hospital_id)

    care_plans = (
        db.query(CarePlan)
        .filter(
            CarePlan.patient_id == patient_id,
            CarePlan.hospital_id == hospital_id
        )
        .all()
    )

    return [
        {
            "id": care_plan.id,
            "title": care_plan.title,
            "description": care_plan.description,
            "status": care_plan.status,
        }
        for care_plan in care_plans
    ]