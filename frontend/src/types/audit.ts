export interface AuditLog {
  id: number
  hospital_id: number | null
  user_id: number | null
  patient_id: number | null
  call_id: number | null

  action: string

  entity_type: string | null
  entity_id: number | null

  correlation_id: string | null

  details: string | null

  created_at: string
}
