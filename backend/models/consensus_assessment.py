from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class ConsensusAssessment(Base):
    __tablename__ = "consensus_assessments"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "call_id",
            name="uq_consensus_hospital_call",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

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

    assessment_a: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    assessment_b: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    consensus_reached: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    disagreement: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    disagreement_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    final_risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    final_action: Mapped[str] = mapped_column(
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

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
