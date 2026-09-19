import apiClient from "./client"
import { MOCK_HOSPITAL_ANALYTICS } from "../mock/mockData"

export interface HospitalAnalytics {
  total_patients: number
  total_campaigns: number
  total_calls: number
  active_calls: number

  risk_distribution: {
    low: number
    medium: number
    high: number
    critical: number
  }

  escalations?: {
    total: number
    open: number
    in_review: number
    resolved: number
    closed: number
    critical: number
    high: number
    medium: number
    low: number
  }

  total_escalations?: number
}

export interface CampaignAnalytics {
  campaign_id: number
  total_queue_items: number

  status_counts?: {
    [key: string]: number
  }

  risk_distribution: {
    low: number
    medium: number
    high: number
    critical: number
  }

  total_escalations?: number
}

export async function getHospitalAnalytics(): Promise<HospitalAnalytics> {
  try {
    const response = await apiClient.get("/analytics/hospital")
    const data = response.data
    if (data && (data.total_patients > 0 || data.total_calls > 0)) {
      if (data.total_escalations === undefined && data.escalations?.total !== undefined) {
        data.total_escalations = data.escalations.total
      }
      return data
    }
    return MOCK_HOSPITAL_ANALYTICS
  } catch {
    return MOCK_HOSPITAL_ANALYTICS
  }
}

export async function getCampaignAnalytics(
  campaignId: number
): Promise<CampaignAnalytics> {
  try {
    const response = await apiClient.get(
      `/analytics/campaign/${campaignId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  return {
    campaign_id: campaignId,
    total_queue_items: 24,
    status_counts: {
      PENDING: 8,
      CALLING: 2,
      CONNECTED: 10,
      ESCALATED: 2,
      COMPLETED: 2,
    },
    risk_distribution: {
      low: 15,
      medium: 6,
      high: 2,
      critical: 1,
    },
    total_escalations: 3,
  }
}
