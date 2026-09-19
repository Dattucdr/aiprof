from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Medication(Base):
    __tablename__ = "medications"

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

    # Medication information
    medication_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    dosage: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    route: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    frequency: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    start_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    end_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
