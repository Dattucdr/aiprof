from datetime import datetime

from sqlalchemy.orm import Session

from models.ai_execution import AIExecution


def start_ai_execution(
    db: Session,
    hospital_id: int,
    operation: str,
    model_name: str | None = None,
    patient_id: int | None = None,
    call_id: int | None = None,
    correlation_id: str | None = None,
):
    execution = AIExecution(
        hospital_id=hospital_id,
        patient_id=patient_id,
        call_id=call_id,
        operation=operation,
        model_name=model_name,
        status="RUNNING",
        correlation_id=correlation_id,
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    return execution


def complete_ai_execution(
    db: Session,
    execution: AIExecution,
    status: str,
    confidence: float | None = None,
    error_message: str | None = None,
):
    execution.status = status
    execution.confidence = confidence
    execution.error_message = error_message
    execution.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(execution)

    return execution
