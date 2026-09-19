import json
from datetime import datetime

from sqlalchemy.orm import Session

from models.patient import Patient


from services.audit_service import create_audit_log


def write_outreach_note_to_mock_ehr(
    db: Session,
    hospital_id: int,
    patient_id: int,
    documentation,
):
    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.hospital_id == hospital_id,
        )
        .first()
    )

    if not patient:
        raise ValueError(
            "Patient not found"
        )

    symptoms_list = json.loads(documentation.symptoms or '[]') if isinstance(documentation.symptoms, str) else (documentation.symptoms or [])
    meds_list = json.loads(documentation.medication_concerns or '[]') if isinstance(documentation.medication_concerns, str) else (documentation.medication_concerns or [])
    questions_list = json.loads(documentation.patient_questions or '[]') if isinstance(documentation.patient_questions, str) else (documentation.patient_questions or [])
    red_flags_list = json.loads(documentation.red_flags or '[]') if isinstance(documentation.red_flags, str) else (documentation.red_flags or [])

    note = (
        f"Post-discharge outreach "
        f"{datetime.utcnow().isoformat()}\n\n"
        f"Summary:\n"
        f"{documentation.summary}\n\n"
        f"Symptoms:\n"
        f"{', '.join(symptoms_list)}\n\n"
        f"Medication concerns:\n"
        f"{', '.join(meds_list)}\n\n"
        f"Patient questions:\n"
        f"{', '.join(questions_list)}\n\n"
        f"Red flags:\n"
        f"{', '.join(red_flags_list)}\n\n"
        f"Triage risk:\n"
        f"{documentation.triage_risk_level}\n\n"
        f"Recommended action:\n"
        f"{documentation.recommended_action}"
    )

    create_audit_log(
        db=db,
        hospital_id=hospital_id,
        patient_id=patient_id,
        call_id=documentation.call_id,
        action="DOCUMENTATION_WRITTEN_TO_EHR",
        entity_type="OUTREACH_DOCUMENTATION",
        entity_id=documentation.id,
        details={
            "written_to_mock_ehr": True,
            "triage_risk_level": documentation.triage_risk_level,
        },
    )

    return {
        "patient_id": patient_id,
        "hospital_id": hospital_id,
        "written_to_mock_ehr": True,
        "note": note,
    }

