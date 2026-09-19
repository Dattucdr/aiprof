from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class CarePlan(Base):
    __tablename__ = "care_plans"

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

    # Care plan information
    title: Mapped[str] = mapped_column(
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
        default="ACTIVE"
    )

    goals: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    follow_up_instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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
