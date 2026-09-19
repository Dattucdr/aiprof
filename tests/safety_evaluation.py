from tests.safety_dataset import SAFETY_DATASET


ESCALATION_ACTIONS = {
    "CLINICAL_REVIEW",
    "URGENT_CLINICAL_REVIEW",
}


def is_escalation_required(
    final_action: str,
) -> bool:
    return final_action in ESCALATION_ACTIONS


def calculate_confusion_matrix(
    predictions: list[bool],
    ground_truth: list[bool],
):
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for predicted, actual in zip(
        predictions,
        ground_truth,
    ):
        if predicted and actual:
            tp += 1
        elif not predicted and not actual:
            tn += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1

    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
    }


def calculate_metrics(
    confusion_matrix: dict,
):
    tp = confusion_matrix["TP"]
    tn = confusion_matrix["TN"]
    fp = confusion_matrix["FP"]
    fn = confusion_matrix["FN"]

    total = tp + tn + fp + fn

    accuracy = (
        (tp + tn) / total
        if total
        else 0.0
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )

    false_negative_rate = (
        fn / (fn + tp)
        if (fn + tp)
        else 0.0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn)
        else 0.0
    )

    return {
        "accuracy": round(
            accuracy,
            4,
        ),
        "precision": round(
            precision,
            4,
        ),
        "recall": round(
            recall,
            4,
        ),
        "false_negative_rate": round(
            false_negative_rate,
            4,
        ),
        "false_positive_rate": round(
            false_positive_rate,
            4,
        ),
    }


def test_confusion_matrix():
    predictions = [
        True,
        False,
        True,
        True,
        False,
    ]

    ground_truth = [
        True,
        False,
        True,
        True,
        False,
    ]

    result = calculate_confusion_matrix(
        predictions,
        ground_truth,
    )

    assert result["TP"] == 3
    assert result["TN"] == 2
    assert result["FP"] == 0
    assert result["FN"] == 0
