from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class AIExecution(Base):
    __tablename__ = "ai_executions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id"),
        nullable=True,
        index=True,
    )

    call_id: Mapped[int | None] = mapped_column(
        ForeignKey("calls.id"),
        nullable=True,
        index=True,
    )

    operation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
