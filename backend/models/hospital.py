from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Asia/Kolkata"
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ACTIVE"
    )

    # Contact information
    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    # Calling configuration
    calling_start_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="09:00"
    )

    calling_end_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="18:00"
    )

    outbound_capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5
    )

    # Retry configuration
    max_retry_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3
    )

    retry_backoff_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30
    )

    # Hospital operational configuration
    outreach_protocols: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    escalation_contacts: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    notification_preferences: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    knowledge_resources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Mock EHR configuration
    mock_ehr_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )