from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.hospital import Hospital
from models.user import User

from auth.authorization import require_roles
from auth.roles import UserRole
from core.tenant import get_tenant_id


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)


@router.get("/me")
def get_my_hospital(
    hospital_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )

    return hospital


@router.put("/me")
def update_my_hospital(
    contact_email: str | None = None,
    contact_phone: str | None = None,
    calling_start_time: str | None = None,
    calling_end_time: str | None = None,
    outbound_capacity: int | None = None,
    max_retry_attempts: int | None = None,
    retry_backoff_minutes: int | None = None,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN
        )
    ),
    db: Session = Depends(get_db)
):
    hospital = db.query(Hospital).filter(
        Hospital.id == hospital_id
    ).first()

    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )

    if contact_email is not None:
        hospital.contact_email = contact_email

    if contact_phone is not None:
        hospital.contact_phone = contact_phone

    if calling_start_time is not None:
        hospital.calling_start_time = calling_start_time

    if calling_end_time is not None:
        hospital.calling_end_time = calling_end_time

    if outbound_capacity is not None:
        hospital.outbound_capacity = outbound_capacity

    if max_retry_attempts is not None:
        hospital.max_retry_attempts = max_retry_attempts

    if retry_backoff_minutes is not None:
        hospital.retry_backoff_minutes = retry_backoff_minutes

    db.commit()
    db.refresh(hospital)

    return hospital
