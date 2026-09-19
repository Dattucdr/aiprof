from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Condition(Base):
    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True
    )

    encounter_id: Mapped[int | None] = mapped_column(
        ForeignKey("encounters.id"),
        nullable=True,
        index=True
    )

    # Condition information
    condition_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    clinical_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ACTIVE"
    )

    severity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    onset_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    resolved_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
