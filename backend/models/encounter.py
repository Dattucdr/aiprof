from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Encounter(Base):
    __tablename__ = "encounters"

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

    # Encounter information
    encounter_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    admission_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    discharge_datetime: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    discharge_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Clinical summary
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    discharge_instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
