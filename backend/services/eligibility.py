import json
from datetime import datetime, timezone

from models.campaign import Campaign
from models.patient import Patient
from models.encounter import Encounter


def check_patient_eligibility(
    patient: Patient,
    campaign: Campaign,
    db
):
    reasons = []

    if not patient.is_active:
        return {
            "patient_id": patient.id,
            "eligible": False,
            "reasons": ["Patient is inactive"]
        }

    rules = {}

    if campaign.rules:
        try:
            rules = json.loads(campaign.rules)
        except json.JSONDecodeError:
            return {
                "patient_id": patient.id,
                "eligible": False,
                "reasons": ["Campaign rules are invalid JSON"]
            }

    require_consent = rules.get(
        "require_consent",
        True
    )

    require_phone_number = rules.get(
        "require_phone_number",
        True
    )

    require_discharge = rules.get(
        "require_discharge",
        True
    )

    min_days = rules.get(
        "min_days_after_discharge",
        0
    )

    max_days = rules.get(
        "max_days_after_discharge",
        campaign.follow_up_window_days
    )

    if require_consent and not patient.communication_consent:
        reasons.append(
            "Patient does not have communication consent"
        )

    if require_phone_number and not patient.phone_number:
        reasons.append(
            "Patient does not have a phone number"
        )

    encounter = db.query(Encounter).filter(
        Encounter.patient_id == patient.id,
        Encounter.hospital_id == campaign.hospital_id,
        Encounter.discharge_datetime.is_not(None)
    ).order_by(
        Encounter.discharge_datetime.desc()
    ).first()

    if require_discharge and not encounter:
        reasons.append(
            "Patient has no discharge record"
        )

    if encounter:
        now = datetime.now(timezone.utc)

        discharge_datetime = encounter.discharge_datetime

        if discharge_datetime.tzinfo is None:
            discharge_datetime = discharge_datetime.replace(
                tzinfo=timezone.utc
            )

        days_since_discharge = (
            now - discharge_datetime
        ).total_seconds() / 86400

        if days_since_discharge < min_days:
            reasons.append(
                "Patient is before the campaign follow-up window"
            )

        if days_since_discharge > max_days:
            reasons.append(
                "Patient is outside the campaign follow-up window"
            )

    eligible = len(reasons) == 0

    if eligible:
        reasons.append(
            "Patient satisfies campaign eligibility rules"
        )

    return {
        "patient_id": patient.id,
        "eligible": eligible,
        "reasons": reasons
    }
