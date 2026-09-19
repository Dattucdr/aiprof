from celery import Celery
from core.config import settings

redis_url = getattr(settings, "REDIS_URL", getattr(settings, "redis_url", "redis://localhost:6379/0"))

celery_app = Celery(
    "aiprof_healthcare",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    beat_schedule={
        "process-retries-every-minute": {
            "task": "process_retries",
            "schedule": 60.0,
        },
        "process-callbacks-every-minute": {
            "task": "process_callbacks",
            "schedule": 60.0,
        },
    },
)

import workers.call_worker
import workers.retry_worker
import workers.callback_worker
import workers.ehr_worker
import workers.outreach_worker
