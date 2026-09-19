from ai.graph.consensus import run_consensus
from ai.schemas.consensus import EscalationAssessment


def make_assessment(
    assessor,
    risk_level,
    action,
    evidence=None,
    red_flags=None,
):
    return EscalationAssessment(
        assessor=assessor,
        risk_level=risk_level,
        recommended_action=action,
        evidence=evidence or [],
        red_flags=red_flags or [],
        confidence=0.9,
    )


def test_exact_agreement():

    assessment_a = make_assessment(
        "ASSESSOR_A",
        "LOW",
        "NO_ACTION",
        ["Patient reports feeling well"],
    )

    assessment_b = make_assessment(
        "ASSESSOR_B",
        "LOW",
        "NO_ACTION",
        ["No concerning symptoms reported"],
    )

    result = run_consensus(
        assessment_a,
        assessment_b,
    )

    assert result.consensus_reached is True
    assert result.disagreement is False
    assert result.final_risk_level == "LOW"
    assert result.final_action == "NO_ACTION"


def test_risk_disagreement_uses_higher_risk():

    assessment_a = make_assessment(
        "ASSESSOR_A",
        "MEDIUM",
        "FOLLOW_UP",
    )

    assessment_b = make_assessment(
        "ASSESSOR_B",
        "HIGH",
        "CLINICAL_REVIEW",
    )

    result = run_consensus(
        assessment_a,
        assessment_b,
    )

    assert result.consensus_reached is False
    assert result.disagreement is True
    assert result.final_risk_level == "HIGH"
    assert result.final_action == "CLINICAL_REVIEW"


def test_action_disagreement_uses_more_conservative_action():

    assessment_a = make_assessment(
        "ASSESSOR_A",
        "HIGH",
        "CLINICAL_REVIEW",
    )

    assessment_b = make_assessment(
        "ASSESSOR_B",
        "HIGH",
        "URGENT_CLINICAL_REVIEW",
    )

    result = run_consensus(
        assessment_a,
        assessment_b,
    )

    assert result.disagreement is True
    assert result.final_risk_level == "HIGH"
    assert result.final_action == "URGENT_CLINICAL_REVIEW"


def test_red_flags_are_merged():

    assessment_a = make_assessment(
        "ASSESSOR_A",
        "LOW",
        "NO_ACTION",
    )

    assessment_b = make_assessment(
        "ASSESSOR_B",
        "HIGH",
        "URGENT_CLINICAL_REVIEW",
        red_flags=["difficulty breathing"],
    )

    result = run_consensus(
        assessment_a,
        assessment_b,
    )

    assert result.disagreement is True
    assert "difficulty breathing" in result.red_flags
    assert result.final_risk_level == "HIGH"
    assert result.final_action == "URGENT_CLINICAL_REVIEW"


def test_evidence_is_merged_without_duplicates():

    assessment_a = make_assessment(
        "ASSESSOR_A",
        "MEDIUM",
        "FOLLOW_UP",
        evidence=["fatigue", "medication concern"],
    )

    assessment_b = make_assessment(
        "ASSESSOR_B",
        "MEDIUM",
        "FOLLOW_UP",
        evidence=["fatigue", "patient question"],
    )

    result = run_consensus(
        assessment_a,
        assessment_b,
    )

    assert result.consensus_reached is True
    assert result.evidence == [
        "fatigue",
        "medication concern",
        "patient question",
    ]
