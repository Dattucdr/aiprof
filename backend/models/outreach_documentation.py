from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class OutreachDocumentation(Base):
    __tablename__ = "outreach_documentations"

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

    triage_assessment_id: Mapped[int | None] = mapped_column(
        ForeignKey("triage_assessments.id"),
        nullable=True,
        index=True,
    )

    consensus_assessment_id: Mapped[int | None] = mapped_column(
        ForeignKey("consensus_assessments.id"),
        nullable=True,
        index=True,
    )

    escalation_id: Mapped[int | None] = mapped_column(
        ForeignKey("escalations.id"),
        nullable=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    symptoms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    medication_concerns: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient_questions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    red_flags: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    triage_risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    escalation_created: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    escalation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    follow_up_required: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    follow_up_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
