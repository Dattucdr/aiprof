from workers.celery_app import celery_app

from database.database import SessionLocal

from services.outreach_orchestrator import (
    run_outreach_orchestration,
)


@celery_app.task(
    bind=True,
    name="run_outreach_orchestration",
    max_retries=2,
)
def run_outreach_orchestration_task(
    self,
    hospital_id: int,
    call_id: int,
):
    db = SessionLocal()

    try:
        result = run_outreach_orchestration(
            db=db,
            hospital_id=hospital_id,
            call_id=call_id,
        )

        return result

    except Exception as exc:

        raise self.retry(
            exc=exc,
            countdown=60,
        )

    finally:
        db.close()
