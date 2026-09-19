export type QueueStatus =
  | "PENDING"
  | "SCHEDULED"
  | "CALLING"
  | "CONNECTED"
  | "NO_ANSWER"
  | "BUSY"
  | "VOICEMAIL"
  | "DROPPED"
  | "RETRY_SCHEDULED"
  | "CALLBACK_SCHEDULED"
  | "ESCALATED"
  | "MANUAL_FOLLOW_UP"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"

export interface QueueItem {
  id: number
  hospital_id: number
  campaign_id: number
  patient_id: number

  status: QueueStatus

  priority_score: number

  scheduled_at: string | null
  deadline_at: string | null

  attempt_count: number
  next_attempt_at: string | null
  callback_at: string | null

  locked_at: string | null
  worker_id: string | null
  worker_heartbeat_at: string | null

  created_at: string
  updated_at: string
}

export interface QueueSummary {
  total: number
  pending: number
  scheduled: number
  calling: number
  completed: number
  failed: number
  escalated: number
  retry_scheduled: number
  callback_scheduled: number
}
