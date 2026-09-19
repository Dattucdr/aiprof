from pydantic import BaseModel, Field


class CampaignAnalytics(BaseModel):
    campaign_id: int

    total_queue_items: int = 0

    pending: int = 0
    scheduled: int = 0
    calling: int = 0

    connected: int = 0
    completed: int = 0

    no_answer: int = 0
    busy: int = 0
    voicemail: int = 0
    dropped: int = 0

    retry_scheduled: int = 0
    callback_scheduled: int = 0

    escalated: int = 0
    failed: int = 0
    cancelled: int = 0


class RiskDistribution(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class EscalationAnalytics(BaseModel):
    total: int = 0
    open: int = 0
    in_review: int = 0
    resolved: int = 0
    closed: int = 0

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class HospitalAnalytics(BaseModel):
    total_patients: int = 0
    active_patients: int = 0

    total_campaigns: int = 0
    running_campaigns: int = 0

    total_calls: int = 0
    completed_calls: int = 0

    active_calls: int = 0

    risk_distribution: RiskDistribution

    escalations: EscalationAnalytics
