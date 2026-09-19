from sqlalchemy.orm import Session

from models.hospital import Hospital


def get_hospital_protocol(
    db: Session,
    hospital_id: int
):
    hospital = (
        db.query(Hospital)
        .filter(
            Hospital.id == hospital_id
        )
        .first()
    )

    if not hospital:
        raise ValueError("Hospital not found")

    return {
        "hospital_id": hospital.id,
        "outreach_protocols": hospital.outreach_protocols,
        "escalation_contacts": hospital.escalation_contacts,
        "notification_preferences": hospital.notification_preferences,
        "knowledge_resources": hospital.knowledge_resources,
    }