from ai.schemas.consensus import (
    EscalationAssessment,
    ConsensusResult,
    validate_assessment,
    validate_consensus,
)
from ai.graph.red_flag_rules import enforce_red_flag_safety

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
ACTION_ORDER = {"NO_ACTION": 0, "FOLLOW_UP": 1, "CLINICAL_REVIEW": 2, "URGENT_CLINICAL_REVIEW": 3}

def get_higher_risk(risk_a: str, risk_b: str) -> str:
    if RISK_ORDER[risk_a] >= RISK_ORDER[risk_b]:
        return risk_a
    return risk_b

def get_higher_action(action_a: str, action_b: str) -> str:
    if ACTION_ORDER[action_a] >= ACTION_ORDER[action_b]:
        return action_a
    return action_b

def merge_unique(items_a: list[str], items_b: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items_a + items_b:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            result.append(normalized)
    return result

def build_disagreement_reason(
    assessment_a: EscalationAssessment,
    assessment_b: EscalationAssessment,
) -> str | None:
    reasons = []
    if assessment_a.risk_level != assessment_b.risk_level:
        reasons.append(f"Risk disagreement: A={assessment_a.risk_level}, B={assessment_b.risk_level}")
    if assessment_a.recommended_action != assessment_b.recommended_action:
        reasons.append(f"Action disagreement: A={assessment_a.recommended_action}, B={assessment_b.recommended_action}")

    red_flags_a = {flag.lower().strip() for flag in assessment_a.red_flags if flag.strip()}
    red_flags_b = {flag.lower().strip() for flag in assessment_b.red_flags if flag.strip()}

    if red_flags_a != red_flags_b:
        reasons.append("Red-flag disagreement between assessors")

    if not reasons:
        return None
    return "; ".join(reasons)

def run_consensus(
    assessment_a: EscalationAssessment,
    assessment_b: EscalationAssessment,
) -> ConsensusResult:
    validate_assessment(assessment_a)
    validate_assessment(assessment_b)

    merged_evidence = merge_unique(assessment_a.evidence, assessment_b.evidence)
    merged_red_flags = merge_unique(assessment_a.red_flags, assessment_b.red_flags)

    disagreement_reason = build_disagreement_reason(assessment_a, assessment_b)
    disagreement = disagreement_reason is not None
    consensus_reached = not disagreement

    final_risk_level = get_higher_risk(assessment_a.risk_level, assessment_b.risk_level)
    final_action = get_higher_action(assessment_a.recommended_action, assessment_b.recommended_action)

    final_risk_level, final_action = enforce_red_flag_safety(
        final_risk_level,
        final_action,
        merged_red_flags,
    )

    result = ConsensusResult(
        assessments=[assessment_a, assessment_b],
        consensus_reached=consensus_reached,
        final_risk_level=final_risk_level,
        final_action=final_action,
        disagreement=disagreement,
        disagreement_reason=disagreement_reason,
        evidence=merged_evidence,
        red_flags=merged_red_flags,
    )

    validate_consensus(result)
    return result
