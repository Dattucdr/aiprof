from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from models.user import User

from tests.safety_dataset import SAFETY_DATASET
from tests.safety_evaluation import (
    calculate_confusion_matrix,
    calculate_metrics,
)


router = APIRouter(
    prefix="/safety",
    tags=["Safety Evaluation"],
)


@router.get("/evaluation")
def get_safety_evaluation(
    current_user: User = Depends(get_current_user),
):
    y_true = []
    y_pred = []

    for case in SAFETY_DATASET:
        y_true.append(
            case["expected_escalation"]
        )

        y_pred.append(
            case["predicted_escalation"]
        )

    confusion = calculate_confusion_matrix(
        y_true,
        y_pred,
    )

    metrics = calculate_metrics(
        confusion
    )

    return {
        "dataset_size": len(SAFETY_DATASET),

        "confusion_matrix": confusion,

        "metrics": metrics,

        "evaluation_type": "DEMONSTRATION",

        "warning": (
            "These results use the synthetic demonstration "
            "dataset and are not production model performance."
        ),
    }
