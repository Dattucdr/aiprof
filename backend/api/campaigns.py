from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.campaign import Campaign
from schemas.campaign import CampaignCreate, CampaignResponse, CampaignStatusUpdate, CampaignPreviewResponse
from services.campaign_service import transition_campaign
from auth.dependencies import get_current_user
from auth.roles import UserRole
from auth.authorization import require_roles
from core.tenant import get_tenant_id
from models.user import User
from models.patient import Patient
from services.eligibility import check_patient_eligibility


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED
)
def create_campaign(
    campaign_data: CampaignCreate,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN,
            UserRole.CAMPAIGN_MANAGER
        )
    ),
    db: Session = Depends(get_db)
):
    campaign = Campaign(
        hospital_id=hospital_id,
        **campaign_data.model_dump()
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return campaign


@router.get(
    "",
    response_model=list[CampaignResponse]
)
def get_campaigns(
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaigns = db.query(Campaign).filter(
        Campaign.hospital_id == hospital_id,
        Campaign.is_active == True
    ).order_by(
        Campaign.created_at.desc()
    ).all()

    return campaigns


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse
)
def get_campaign(
    campaign_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.hospital_id == hospital_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    return campaign


@router.patch(
    "/{campaign_id}/status",
    response_model=CampaignResponse
)
def update_campaign_status(
    campaign_id: int,
    status_data: CampaignStatusUpdate,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN,
            UserRole.CAMPAIGN_MANAGER
        )
    ),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.hospital_id == hospital_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    transition_campaign(
        campaign,
        status_data.status
    )

    db.commit()
    db.refresh(campaign)

    return campaign

@router.get(
    "/{campaign_id}/eligibility"
)
def evaluate_campaign_eligibility(
    campaign_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.hospital_id == hospital_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    patients = db.query(Patient).filter(
        Patient.hospital_id == hospital_id,
        Patient.is_active == True
    ).all()

    results = []

    for patient in patients:
        result = check_patient_eligibility(
            patient=patient,
            campaign=campaign,
            db=db
        )

        results.append(result)

    eligible_count = sum(
        1 for result in results
        if result["eligible"]
    )

    return {
        "campaign_id": campaign.id,
        "campaign_name": campaign.name,
        "total_patients_evaluated": len(results),
        "eligible_count": eligible_count,
        "ineligible_count": len(results) - eligible_count,
        "patients": results
    }


@router.get(
    "/{campaign_id}/preview",
    response_model=CampaignPreviewResponse
)
def preview_campaign(
    campaign_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.hospital_id == hospital_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    patients = db.query(Patient).filter(
        Patient.hospital_id == hospital_id,
        Patient.is_active == True
    ).all()

    eligible_patient_ids = []
    total_patients = len(patients)

    for patient in patients:
        result = check_patient_eligibility(
            patient=patient,
            campaign=campaign,
            db=db
        )

        if result["eligible"]:
            eligible_patient_ids.append(patient.id)

    eligible_count = len(eligible_patient_ids)

    return {
        "campaign_id": campaign.id,
        "campaign_name": campaign.name,
        "campaign_status": campaign.status,
        "total_patients_evaluated": total_patients,
        "eligible_count": eligible_count,
        "ineligible_count": total_patients - eligible_count,
        "eligible_patient_ids": eligible_patient_ids
    }