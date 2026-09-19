from datetime import datetime, timezone

from workers.celery_app import celery_app
from database.database import SessionLocal

from models.queue_item import QueueItem


@celery_app.task(
    name="process_retries"
)
def process_retries():

    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc).replace(
            tzinfo=None
        )

        items = (
            db.query(QueueItem)
            .filter(
                QueueItem.status == "RETRY_SCHEDULED",
                QueueItem.next_attempt_at <= now,
            )
            .all()
        )

        processed = 0

        for item in items:

            item.status = "SCHEDULED"

            processed += 1

        db.commit()

        return {
            "processed": processed
        }

    finally:
        db.close()
