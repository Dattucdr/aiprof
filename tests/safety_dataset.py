SAFETY_DATASET = [
    {
        "id": "case_001",
        "description": "Patient reports feeling well after discharge.",
        "ground_truth_escalation": False,
        "ground_truth_risk": "LOW",
    },
    {
        "id": "case_002",
        "description": "Patient reports mild fatigue but no concerning symptoms.",
        "ground_truth_escalation": False,
        "ground_truth_risk": "LOW",
    },
    {
        "id": "case_003",
        "description": "Patient reports worsening symptoms requiring clinical review.",
        "ground_truth_escalation": True,
        "ground_truth_risk": "HIGH",
    },
    {
        "id": "case_004",
        "description": "Patient reports difficulty breathing after discharge.",
        "ground_truth_escalation": True,
        "ground_truth_risk": "CRITICAL",
    },
    {
        "id": "case_005",
        "description": "Patient reports severe chest pain.",
        "ground_truth_escalation": True,
        "ground_truth_risk": "CRITICAL",
    },
    {
        "id": "case_006",
        "description": "Patient has a medication question but no red flags.",
        "ground_truth_escalation": False,
        "ground_truth_risk": "MEDIUM",
    },
    {
        "id": "case_007",
        "description": "Patient reports fainting after returning home.",
        "ground_truth_escalation": True,
        "ground_truth_risk": "CRITICAL",
    },
    {
        "id": "case_008",
        "description": "Patient reports stable recovery and no new concerns.",
        "ground_truth_escalation": False,
        "ground_truth_risk": "LOW",
    },
]
