from fastapi import HTTPException, status
from models.campaign import Campaign


ALLOWED_TRANSITIONS = {
    "DRAFT": ["READY", "CANCELLED"],
    "READY": ["SCHEDULED", "RUNNING", "CANCELLED"],
    "SCHEDULED": ["RUNNING", "CANCELLED"],
    "RUNNING": ["PAUSED", "COMPLETED"],
    "PAUSED": ["RUNNING", "CANCELLED"],
    "COMPLETED": [],
    "CANCELLED": []
}


def transition_campaign(
    campaign: Campaign,
    new_status: str
):
    current_status = campaign.status

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid campaign transition: "
                f"{current_status} -> {new_status}"
            )
        )

    campaign.status = new_status

    return campaign
