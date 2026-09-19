import json
import uuid

from sqlalchemy.orm import Session

from models.audit_log import AuditLog


def generate_correlation_id() -> str:
    return str(uuid.uuid4())


def create_audit_log(
    db: Session,
    action: str,
    hospital_id: int | None = None,
    user_id: int | None = None,
    patient_id: int | None = None,
    call_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    correlation_id: str | None = None,
    details: dict | None = None,
):
    audit = AuditLog(
        hospital_id=hospital_id,
        user_id=user_id,
        patient_id=patient_id,
        call_id=call_id,

        action=action,

        entity_type=entity_type,
        entity_id=entity_id,

        correlation_id=correlation_id,

        details=json.dumps(
            details or {}
        ),
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def get_hospital_audit_logs(
    db: Session,
    hospital_id: int,
    limit: int = 100,
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.hospital_id == hospital_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


def get_audit_logs_by_patient(
    db: Session,
    patient_id: int,
    hospital_id: int | None = None,
):
    query = db.query(AuditLog).filter(AuditLog.patient_id == patient_id)
    if hospital_id is not None:
        query = query.filter(AuditLog.hospital_id == hospital_id)
    return query.order_by(AuditLog.created_at.desc()).all()


