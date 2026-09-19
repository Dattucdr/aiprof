from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.queue_item import QueueItem
from models.user import User
from schemas.queue import QueueStatusUpdate
from auth.dependencies import get_current_user
from core.tenant import get_tenant_id
from services.queue_service import transition_queue_item
from models.campaign import Campaign
from models.patient import Patient
from services.queue_service import calculate_priority_score
from auth.authorization import require_roles
from auth.roles import UserRole
from services.queue_service import create_queue_items_for_campaign
from services.queue_service import reserve_queue_item
from schemas.queue import QueueStatusUpdate, QueueDispatchResponse


from schemas.queue import (
    QueueStatusUpdate,
    QueueDispatchResponse,
    CallOutcomeRequest,
    CallbackRequest
)

from services.queue_service import (
    dispatch_next_queue_item,
    handle_call_outcome,
    schedule_callback,
    recover_stale_queue_items
)

from services.queue_simulation import (
    create_simulation_patients,
    run_queue_simulation
)
from models.hospital import Hospital

router = APIRouter(
    prefix="/queue",
    tags=["Queue"]
)


@router.get("")
def get_queue_items(
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(QueueItem)
        .filter(QueueItem.hospital_id == hospital_id)
        .order_by(QueueItem.priority_score.desc(), QueueItem.created_at.desc())
        .all()
    )
    return items


@router.get("/campaign/{campaign_id}")
def get_campaign_queue_items(
    campaign_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(QueueItem)
        .filter(
            QueueItem.hospital_id == hospital_id,
            QueueItem.campaign_id == campaign_id
        )
        .order_by(QueueItem.priority_score.desc(), QueueItem.created_at.desc())
        .all()
    )
    return items


@router.get("/patient/{patient_id}")
def get_patient_queue_items(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(QueueItem)
        .filter(
            QueueItem.hospital_id == hospital_id,
            QueueItem.patient_id == patient_id
        )
        .order_by(QueueItem.created_at.desc())
        .all()
    )
    return items


@router.get("/{queue_item_id}")
def get_queue_item_by_id(
    queue_item_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(QueueItem).filter(
        QueueItem.id == queue_item_id,
        QueueItem.hospital_id == hospital_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    return item



@router.patch(
    "/{queue_item_id}/status"
)

def update_queue_status(
    queue_item_id: int,
    status_data: QueueStatusUpdate,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = db.query(QueueItem).filter(
        QueueItem.id == queue_item_id,
        QueueItem.hospital_id == hospital_id
    ).first()

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    transition_queue_item(
        queue_item,
        status_data.status
    )

    db.commit()
    db.refresh(queue_item)

    return queue_item

@router.get(
    "/{queue_item_id}/priority"
)
def get_queue_priority(
    queue_item_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = db.query(QueueItem).filter(
        QueueItem.id == queue_item_id,
        QueueItem.hospital_id == hospital_id
    ).first()

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    campaign = db.query(Campaign).filter(
        Campaign.id == queue_item.campaign_id,
        Campaign.hospital_id == hospital_id
    ).first()

    patient = db.query(Patient).filter(
        Patient.id == queue_item.patient_id,
        Patient.hospital_id == hospital_id
    ).first()

    if not campaign or not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Related campaign or patient not found"
        )

    score = calculate_priority_score(
        campaign=campaign,
        patient=patient,
        queue_item=queue_item
    )

    return {
        "queue_item_id": queue_item.id,
        "patient_id": patient.id,
        "campaign_id": campaign.id,
        "priority_score": score
    }

@router.post(
    "/campaigns/{campaign_id}/populate"
)
def populate_campaign_queue(
    campaign_id: int,
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

    if campaign.status not in ["READY", "SCHEDULED", "RUNNING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Campaign must be READY, SCHEDULED, "
                "or RUNNING before populating the queue"
            )
        )

    result = create_queue_items_for_campaign(
        campaign=campaign,
        hospital_id=hospital_id,
        db=db
    )

    return {
        "campaign_id": campaign.id,
        "created_count": len(result["created_items"]),
        "skipped_count": len(result["skipped_patient_ids"]),
        "skipped_patient_ids": result["skipped_patient_ids"]
    }

@router.post(
    "/{queue_item_id}/reserve"
)
def reserve_queue_item_api(
    queue_item_id: int,
    worker_id: str,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = reserve_queue_item(
        queue_item_id=queue_item_id,
        hospital_id=hospital_id,
        worker_id=worker_id,
        db=db
    )

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Queue item could not be reserved. "
                "It may already be reserved or "
                "hospital capacity may be full."
            )
        )

    return {
        "message": "Queue item reserved successfully",
        "queue_item_id": queue_item.id,
        "status": queue_item.status,
        "worker_id": queue_item.worker_id,
        "attempt_count": queue_item.attempt_count,
        "locked_at": queue_item.locked_at
    }

@router.post(
    "/dispatch-next",
    response_model=QueueDispatchResponse
)
def dispatch_next(
    worker_id: str,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN,
            UserRole.CAMPAIGN_MANAGER
        )
    ),
    db: Session = Depends(get_db)
):
    queue_item = dispatch_next_queue_item(
        hospital_id=hospital_id,
        worker_id=worker_id,
        db=db
    )

    if not queue_item:
        return QueueDispatchResponse(
            reserved=False,
            reason="No callable queue item available or outbound capacity is full"
        )

    return QueueDispatchResponse(
        reserved=True,
        queue_item_id=queue_item.id,
        patient_id=queue_item.patient_id,
        campaign_id=queue_item.campaign_id,
        status=queue_item.status,
        worker_id=queue_item.worker_id,
        priority_score=queue_item.priority_score,
        attempt_count=queue_item.attempt_count,
        locked_at=queue_item.locked_at
    )

@router.post("/{queue_item_id}/outcome")
def process_call_outcome(
    queue_item_id: int,
    outcome_data: CallOutcomeRequest,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = (
        db.query(QueueItem)
        .filter(
            QueueItem.id == queue_item_id,
            QueueItem.hospital_id == hospital_id
        )
        .first()
    )

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )

    try:
        updated_item = handle_call_outcome(
            queue_item=queue_item,
            outcome=outcome_data.outcome,
            hospital=hospital,
            db=db
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return updated_item

@router.post("/{queue_item_id}/callback")
def create_callback(
    queue_item_id: int,
    callback_data: CallbackRequest,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = (
        db.query(QueueItem)
        .filter(
            QueueItem.id == queue_item_id,
            QueueItem.hospital_id == hospital_id
        )
        .first()
    )

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    if queue_item.status != "CONNECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Callback can only be scheduled from a connected call"
        )

    try:
        updated_item = schedule_callback(
            queue_item=queue_item,
            callback_at=callback_data.callback_at,
            db=db
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return updated_item


@router.post("/recover-stale")
def recover_stale(
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN,
            UserRole.CAMPAIGN_MANAGER
        )
    ),
    db: Session = Depends(get_db)
):
    recovered_items = recover_stale_queue_items(
        hospital_id=hospital_id,
        db=db
    )

    return {
        "recovered_count": len(recovered_items),
        "queue_item_ids": [
            item.id for item in recovered_items
        ]
    }


@router.post("/{queue_item_id}/heartbeat")
def queue_heartbeat(
    queue_item_id: int,
    worker_id: str,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = (
        db.query(QueueItem)
        .filter(
            QueueItem.id == queue_item_id,
            QueueItem.hospital_id == hospital_id
        )
        .first()
    )

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    if queue_item.status != "CALLING" or queue_item.worker_id != worker_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Queue item is not currently active for this worker"
        )

    now = datetime.now(timezone.utc)
    queue_item.worker_heartbeat_at = now
    db.commit()
    db.refresh(queue_item)

    return {
        "message": "Heartbeat updated successfully",
        "queue_item_id": queue_item.id,
        "worker_id": queue_item.worker_id,
        "worker_heartbeat_at": queue_item.worker_heartbeat_at
    }

@router.post("/simulation/create")
def create_queue_simulation(
    count: int = 25,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN,
            UserRole.CAMPAIGN_MANAGER
        )
    ),
    db: Session = Depends(get_db)
):
    campaign = (
        db.query(Campaign)
        .filter(
            Campaign.hospital_id == hospital_id,
            Campaign.status == "RUNNING"
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No RUNNING campaign found"
        )

    if count < 20 or count > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation count must be between 20 and 30"
        )

    patients = create_simulation_patients(
        hospital_id=hospital_id,
        campaign_id=campaign.id,
        db=db,
        count=count
    )

    return {
        "message": "Queue simulation created",
        "campaign_id": campaign.id,
        "patient_count": len(patients)
    }


@router.post("/simulation/run")
def run_simulation(
    worker_count: int = 3,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(
        require_roles(
            UserRole.HOSPITAL_ADMIN,
            UserRole.CAMPAIGN_MANAGER
        )
    ),
    db: Session = Depends(get_db)
):
    if worker_count < 1 or worker_count > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="worker_count must be between 1 and 10"
        )

    results = run_queue_simulation(
        hospital_id=hospital_id,
        worker_count=worker_count,
        db=db
    )

    return {
        "processed_count": len(results),
        "worker_count": worker_count,
        "results": results
    }