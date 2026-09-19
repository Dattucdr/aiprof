from ai.graph.consensus import run_consensus
from ai.schemas.consensus import EscalationAssessment


def assessment(
    assessor,
    risk,
    action,
    red_flags=None,
):
    return EscalationAssessment(
        assessor=assessor,
        risk_level=risk,
        recommended_action=action,
        evidence=[],
        red_flags=red_flags or [],
        confidence=0.9,
    )


def test_red_flag_from_one_assessor_is_preserved():
    a = assessment(
        "ASSESSOR_A",
        "LOW",
        "NO_ACTION",
    )

    b = assessment(
        "ASSESSOR_B",
        "HIGH",
        "URGENT_CLINICAL_REVIEW",
        ["difficulty breathing"],
    )

    result = run_consensus(a, b)

    assert (
        "difficulty breathing"
        in result.red_flags
    )

    assert result.final_risk_level == "HIGH"

    assert (
        result.final_action
        == "URGENT_CLINICAL_REVIEW"
    )


def test_disagreement_is_recorded():
    a = assessment(
        "ASSESSOR_A",
        "MEDIUM",
        "FOLLOW_UP",
    )

    b = assessment(
        "ASSESSOR_B",
        "HIGH",
        "CLINICAL_REVIEW",
    )

    result = run_consensus(a, b)

    assert result.disagreement is True
    assert result.consensus_reached is False
    assert result.disagreement_reason is not None
