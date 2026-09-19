from datetime import datetime
from pydantic import BaseModel


class TimelineItem(BaseModel):
    event_type: str
    event_id: int
    event_datetime: datetime | None
    title: str
    description: str | None = None
