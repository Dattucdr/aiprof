from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from database.database import get_db

from auth.dependencies import get_current_user

from core.tenant import get_tenant_id

from models.user import User
from models.queue_item import QueueItem
from models.patient import Patient

from schemas.call import (
    CallCreate,
    CallResponse,
    CallOutcomeRequest
)

from models.call import Call

from services.call_service import (
    create_call,
    finish_call
)
from workers.outreach_worker import (
    run_outreach_orchestration_task,
)


router = APIRouter(
    prefix="/calls",
    tags=["Calls"]
)


@router.post(
    "",
    response_model=CallResponse,
    status_code=status.HTTP_201_CREATED
)
def start_call(
    call_data: CallCreate,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queue_item = (
        db.query(QueueItem)
        .filter(
            QueueItem.id == call_data.queue_item_id,
            QueueItem.hospital_id == hospital_id
        )
        .first()
    )

    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Queue item not found"
        )

    if queue_item.worker_id != call_data.worker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Worker is not assigned to this queue item"
        )

    return create_call(
        queue_item=queue_item,
        worker_id=call_data.worker_id,
        idempotency_key=call_data.idempotency_key,
        db=db
    )

@router.post(
    "/{call_id}/outcome",
    response_model=CallResponse
)
def finish_call_endpoint(
    call_id: int,
    outcome_data: CallOutcomeRequest,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == hospital_id
        )
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    if call.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Call is not in progress"
        )

    return finish_call(
        call=call,
        outcome=outcome_data.outcome,
        notes=outcome_data.notes,
        transcript=outcome_data.transcript,
        db=db
    )


@router.get(
    "",
    response_model=list[CallResponse]
)
def get_calls(
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    calls = (
        db.query(Call)
        .filter(Call.hospital_id == hospital_id)
        .order_by(Call.created_at.desc())
        .all()
    )

    return calls


@router.get(
    "/patient/{patient_id}/history",
    response_model=list[CallResponse]
)
def get_patient_outreach_history(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id,
            Patient.hospital_id == hospital_id
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    calls = (
        db.query(Call)
        .filter(
            Call.patient_id == patient_id,
            Call.hospital_id == hospital_id
        )
        .order_by(Call.created_at.asc())
        .all()
    )

    return calls


@router.get(
    "/patient/{patient_id}",
    response_model=list[CallResponse]
)
def get_patient_calls(
    patient_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    calls = (
        db.query(Call)
        .filter(
            Call.patient_id == patient_id,
            Call.hospital_id == hospital_id
        )
        .order_by(Call.created_at.desc())
        .all()
    )

    return calls


@router.get(
    "/campaign/{campaign_id}",
    response_model=list[CallResponse]
)
def get_campaign_calls(
    campaign_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    calls = (
        db.query(Call)
        .filter(
            Call.campaign_id == campaign_id,
            Call.hospital_id == hospital_id
        )
        .order_by(Call.created_at.desc())
        .all()
    )
@router.get(
    "/queue/{queue_item_id}",
    response_model=list[CallResponse]
)
def get_queue_calls(
    queue_item_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    calls = (
        db.query(Call)
        .filter(
            Call.queue_item_id == queue_item_id,
            Call.hospital_id == hospital_id
        )
        .order_by(Call.attempt_number.asc())
        .all()
    )

    return calls


@router.get(
    "/{call_id}",
    response_model=CallResponse
)
def get_call(
    call_id: int,
    hospital_id: int = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id == hospital_id
        )
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )

    return call


@router.post(
    "/{call_id}/process"
)
def process_completed_call(
    call_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    call = (
        db.query(Call)
        .filter(
            Call.id == call_id,
            Call.hospital_id
            == current_user.hospital_id,
        )
        .first()
    )

    if not call:
        raise HTTPException(
            status_code=404,
            detail="Call not found",
        )

    if call.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=(
                "Call must be completed "
                "before processing"
            ),
        )

    task = (
        run_outreach_orchestration_task.delay(
            current_user.hospital_id,
            call.id,
        )
    )

    return {
        "message": (
            "Outreach processing started"
        ),
        "task_id": task.id,
        "call_id": call.id,
    }