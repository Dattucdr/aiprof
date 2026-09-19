from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from database.database import get_db

from services.analytics_service import (
    get_hospital_analytics,
    get_campaign_analytics,
)
from services.audit_service import (
    get_audit_logs_by_patient,
    get_hospital_audit_logs,
)



router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/hospital")
def hospital_analytics(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    return get_hospital_analytics(
        db=db,
        hospital_id=current_user.hospital_id,
    )


@router.get(
    "/campaign/{campaign_id}"
)
def campaign_analytics(
    campaign_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    return get_campaign_analytics(
        db=db,
        hospital_id=current_user.hospital_id,
        campaign_id=campaign_id,
    )


@router.get("/audit")
def hospital_audit_logs(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    return get_hospital_audit_logs(
        db=db,
        hospital_id=current_user.hospital_id,
    )


@router.get("/audit/{patient_id}")
def patient_audit_logs(
    patient_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    return get_audit_logs_by_patient(
        db=db,
        patient_id=patient_id,
        hospital_id=current_user.hospital_id,
    )


