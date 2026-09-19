from workers.celery_app import celery_app
from database.database import SessionLocal


@celery_app.task(
    bind=True,
    name="process_call",
    max_retries=3,
)
def process_call(
    self,
    queue_item_id: int,
    worker_id: str,
):
    db = SessionLocal()

    try:
        print(
            f"Processing queue item "
            f"{queue_item_id}"
        )

        # The actual call execution layer will
        # be connected here.

        return {
            "queue_item_id": queue_item_id,
            "worker_id": worker_id,
            "status": "PROCESSED",
        }

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=30,
        )

    finally:
        db.close()
