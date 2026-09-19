from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from database.database import Base


class EscalationAssessment(Base):
    __tablename__ = "escalation_assessments"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "call_id",
            "assessor",
            name="uq_escalation_assessment_call_assessor",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id"),
        nullable=False,
        index=True,
    )

    queue_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("queue_items.id"),
        nullable=True,
        index=True,
    )

    assessor: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    red_flags: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
