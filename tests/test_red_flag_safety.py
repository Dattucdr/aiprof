from ai.graph.red_flag_rules import (
    detect_red_flags,
    enforce_red_flag_safety,
)


def test_difficulty_breathing_is_detected():
    text = (
        "The patient reports "
        "difficulty breathing."
    )

    red_flags = detect_red_flags(text)

    assert len(red_flags) > 0


def test_chest_pain_is_detected():
    text = (
        "Patient reports severe chest pain."
    )

    red_flags = detect_red_flags(text)

    assert len(red_flags) > 0


def test_red_flag_cannot_result_in_no_action():
    risk, action = enforce_red_flag_safety(
        "LOW",
        "NO_ACTION",
        ["difficulty breathing"],
    )

    assert risk == "HIGH"
    assert action == "URGENT_CLINICAL_REVIEW"


def test_red_flag_regression_cases():
    from tests.red_flag_cases import RED_FLAG_REGRESSION_CASES

    for case in RED_FLAG_REGRESSION_CASES:
        result = detect_red_flags(case["text"])
        detected = len(result) > 0

        assert detected == case["expected"], (
            f"Failed case: {case['text']}"
        )

