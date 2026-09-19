from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class QueueItem(Base):
    __tablename__ = "queue_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True
    )

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True
    )

    priority_score: Mapped[float] = mapped_column(
        nullable=False,
        default=0
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    deadline_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    callback_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    locked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    worker_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    worker_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
