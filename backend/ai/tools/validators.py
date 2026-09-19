from typing import Any

def validate_patient_id(patient_id: int):
    if not isinstance(patient_id, int) or patient_id <= 0:
        raise ValueError("Invalid patient ID")
    return patient_id

def validate_hospital_id(hospital_id: int):
    if not isinstance(hospital_id, int) or hospital_id <= 0:
        raise ValueError("Invalid hospital ID")
    return hospital_id

def validate_escalation_priority(priority: str):
    allowed_priorities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if priority not in allowed_priorities:
        raise ValueError("Invalid escalation priority")
    return priority

def validate_required_text(value: Any, field_name: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()
