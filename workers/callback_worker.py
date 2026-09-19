from datetime import datetime, timezone

from workers.celery_app import celery_app
from database.database import SessionLocal

from models.queue_item import QueueItem


@celery_app.task(
    name="process_callbacks"
)
def process_callbacks():

    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc).replace(
            tzinfo=None
        )

        items = (
            db.query(QueueItem)
            .filter(
                QueueItem.status == "CALLBACK_SCHEDULED",
                QueueItem.callback_at <= now,
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
