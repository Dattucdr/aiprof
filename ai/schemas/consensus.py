from pydantic import BaseModel, Field


ALLOWED_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
}


ALLOWED_ACTIONS = {
    "NO_ACTION",
    "FOLLOW_UP",
    "CLINICAL_REVIEW",
    "URGENT_CLINICAL_REVIEW"
}


class EscalationAssessment(BaseModel):
    assessor: str

    risk_level: str

    recommended_action: str

    evidence: list[str] = Field(
        default_factory=list
    )

    red_flags: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


class ConsensusResult(BaseModel):
    assessments: list[EscalationAssessment]

    consensus_reached: bool

    final_risk_level: str

    final_action: str

    disagreement: bool

    disagreement_reason: str | None = None

    evidence: list[str] = Field(
        default_factory=list
    )

    red_flags: list[str] = Field(
        default_factory=list
    )


def validate_assessment(
    assessment: EscalationAssessment
) -> EscalationAssessment:

    if assessment.risk_level not in ALLOWED_RISK_LEVELS:
        raise ValueError(
            f"Invalid risk level: {assessment.risk_level}"
        )

    if assessment.recommended_action not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Invalid recommended action: "
            f"{assessment.recommended_action}"
        )

    return assessment


def validate_consensus(
    result: ConsensusResult
) -> ConsensusResult:

    if result.final_risk_level not in ALLOWED_RISK_LEVELS:
        raise ValueError(
            f"Invalid final risk level: "
            f"{result.final_risk_level}"
        )

    if result.final_action not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Invalid final action: "
            f"{result.final_action}"
        )

    return result
