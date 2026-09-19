from sqlalchemy.orm import Session

from models.patient import Patient
from models.campaign import Campaign
from models.queue_item import QueueItem
from models.call import Call
from models.triage_assessment import TriageAssessment
from models.escalation import Escalation

from schemas.analytics import (
    CampaignAnalytics,
    RiskDistribution,
    EscalationAnalytics,
    HospitalAnalytics,
)


def get_risk_distribution(
    db: Session,
    hospital_id: int,
):
    assessments = (
        db.query(TriageAssessment)
        .filter(
            TriageAssessment.hospital_id
            == hospital_id
        )
        .all()
    )

    result = RiskDistribution()

    for assessment in assessments:

        risk = assessment.risk_level.upper()

        if risk == "LOW":
            result.low += 1

        elif risk == "MEDIUM":
            result.medium += 1

        elif risk == "HIGH":
            result.high += 1

        elif risk == "CRITICAL":
            result.critical += 1

    return result


def get_escalation_analytics(
    db: Session,
    hospital_id: int,
):
    escalations = (
        db.query(Escalation)
        .filter(
            Escalation.hospital_id
            == hospital_id
        )
        .all()
    )

    result = EscalationAnalytics()

    result.total = len(escalations)

    for escalation in escalations:

        status = escalation.status.upper()
        priority = escalation.priority.upper()

        if status == "OPEN":
            result.open += 1

        elif status == "IN_REVIEW":
            result.in_review += 1

        elif status == "RESOLVED":
            result.resolved += 1

        elif status == "CLOSED":
            result.closed += 1

        if priority == "CRITICAL":
            result.critical += 1

        elif priority == "HIGH":
            result.high += 1

        elif priority == "MEDIUM":
            result.medium += 1

        elif priority == "LOW":
            result.low += 1

    return result


def get_campaign_analytics(
    db: Session,
    hospital_id: int,
    campaign_id: int,
):
    items = (
        db.query(QueueItem)
        .filter(
            QueueItem.hospital_id == hospital_id,
            QueueItem.campaign_id == campaign_id,
        )
        .all()
    )

    result = CampaignAnalytics(
        campaign_id=campaign_id
    )

    result.total_queue_items = len(items)

    for item in items:

        status = item.status.upper()

        if status == "PENDING":
            result.pending += 1

        elif status == "SCHEDULED":
            result.scheduled += 1

        elif status == "CALLING":
            result.calling += 1

        elif status == "CONNECTED":
            result.connected += 1

        elif status == "COMPLETED":
            result.completed += 1

        elif status == "NO_ANSWER":
            result.no_answer += 1

        elif status == "BUSY":
            result.busy += 1

        elif status == "VOICEMAIL":
            result.voicemail += 1

        elif status == "DROPPED":
            result.dropped += 1

        elif status == "RETRY_SCHEDULED":
            result.retry_scheduled += 1

        elif status == "CALLBACK_SCHEDULED":
            result.callback_scheduled += 1

        elif status == "ESCALATED":
            result.escalated += 1

        elif status == "FAILED":
            result.failed += 1

        elif status == "CANCELLED":
            result.cancelled += 1

    return result


def get_hospital_analytics(
    db: Session,
    hospital_id: int,
):
    total_patients = (
        db.query(Patient)
        .filter(
            Patient.hospital_id == hospital_id
        )
        .count()
    )

    active_patients = (
        db.query(Patient)
        .filter(
            Patient.hospital_id == hospital_id,
            Patient.is_active.is_(True),
        )
        .count()
    )

    total_campaigns = (
        db.query(Campaign)
        .filter(
            Campaign.hospital_id == hospital_id
        )
        .count()
    )

    running_campaigns = (
        db.query(Campaign)
        .filter(
            Campaign.hospital_id == hospital_id,
            Campaign.status == "RUNNING",
        )
        .count()
    )

    total_calls = (
        db.query(Call)
        .filter(
            Call.hospital_id == hospital_id
        )
        .count()
    )

    completed_calls = (
        db.query(Call)
        .filter(
            Call.hospital_id == hospital_id,
            Call.status == "COMPLETED",
        )
        .count()
    )

    active_calls = (
        db.query(Call)
        .filter(
            Call.hospital_id == hospital_id,
            Call.status == "IN_PROGRESS",
        )
        .count()
    )

    return HospitalAnalytics(
        total_patients=total_patients,
        active_patients=active_patients,

        total_campaigns=total_campaigns,
        running_campaigns=running_campaigns,

        total_calls=total_calls,
        completed_calls=completed_calls,

        active_calls=active_calls,

        risk_distribution=(
            get_risk_distribution(
                db,
                hospital_id,
            )
        ),

        escalations=(
            get_escalation_analytics(
                db,
                hospital_id,
            )
        ),
    )
