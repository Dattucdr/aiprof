export type CampaignStatus =
  | "DRAFT"
  | "READY"
  | "SCHEDULED"
  | "RUNNING"
  | "PAUSED"
  | "COMPLETED"
  | "CANCELLED"

export interface Campaign {
  id: number
  hospital_id: number
  name: string
  description: string | null
  status: CampaignStatus
  priority: number
  follow_up_window_days: number
  max_retry_attempts: number | null
  rules: string | null
  calling_start: string | null
  calling_end: string | null
  is_active: boolean
  scheduled_at: string | null
  created_at: string
  updated_at: string
}
