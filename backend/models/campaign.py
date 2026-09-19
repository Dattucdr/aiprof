from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="DRAFT",
        index=True
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5
    )

    follow_up_window_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=7
    )

    max_retry_attempts: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    rules: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    calling_start_time: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    calling_end_time: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
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
