from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Observation(Base):
    __tablename__ = "observations"

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

    # Observation details
    observation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    value: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="FINAL"
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
