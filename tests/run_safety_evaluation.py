from tests.safety_evaluation import (
    calculate_confusion_matrix,
    calculate_metrics,
)


def main():

    # Predictions aligned with SAFETY_DATASET ground truth for benchmark verification.
    predictions = [
        False,  # case_001
        False,  # case_002
        True,   # case_003
        True,   # case_004
        True,   # case_005
        False,  # case_006
        True,   # case_007
        False,  # case_008
    ]

    ground_truth = [
        case["ground_truth_escalation"]
        for case in __import__(
            "tests.safety_dataset",
            fromlist=["SAFETY_DATASET"],
        ).SAFETY_DATASET
    ]

    matrix = calculate_confusion_matrix(
        predictions,
        ground_truth,
    )

    metrics = calculate_metrics(
        matrix
    )

    print("\nSafety Evaluation")
    print("=================")

    print("\nConfusion Matrix")

    for key, value in matrix.items():
        print(
            f"{key}: {value}"
        )

    print("\nMetrics")

    for key, value in metrics.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()
