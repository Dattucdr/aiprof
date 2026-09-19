RED_FLAG_TERMS = [
    "severe chest pain",
    "difficulty breathing",
    "shortness of breath",
    "fainting",
    "unconscious",
    "severe bleeding",
    "confusion",
    "stroke",
]

def detect_red_flags(text: str) -> list[str]:
    text_lower = text.lower()
    detected = []
    for term in RED_FLAG_TERMS:
        if term in text_lower:
            detected.append(term)
    return detected

def enforce_red_flag_safety(
    risk_level: str,
    recommended_action: str,
    red_flags: list[str]
):
    if not red_flags:
        return risk_level, recommended_action

    if risk_level in {"LOW", "MEDIUM"}:
        risk_level = "HIGH"

    if recommended_action in {"NO_ACTION", "FOLLOW_UP"}:
        recommended_action = "URGENT_CLINICAL_REVIEW"

    return risk_level, recommended_action
