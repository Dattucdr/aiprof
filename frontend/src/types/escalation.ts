export interface Escalation {
  id: number
  hospital_id: number
  patient_id: number
  queue_item_id: number | null
  call_id: number | null
  consensus_assessment_id: number | null

  reason: string
  priority: string
  evidence: string | null

  status: string
  source: string

  final_action: string | null

  resolved_at: string | null
  resolution_notes: string | null

  created_at: string
  updated_at: string
}

export type EscalationPriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
export type EscalationStatus = "OPEN" | "IN_REVIEW" | "RESOLVED" | "CLOSED"

export interface EscalationStatusUpdate {
  status: EscalationStatus
  resolution_notes?: string
}
