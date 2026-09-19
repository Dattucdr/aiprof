export interface OutreachDocumentation {
  id: number

  hospital_id: number
  patient_id: number
  call_id: number

  triage_assessment_id: number | null
  consensus_assessment_id: number | null
  escalation_id: number | null

  summary: string

  symptoms: string
  medication_concerns: string
  patient_questions: string
  red_flags: string

  triage_risk_level: string
  recommended_action: string

  escalation_created: boolean
  escalation_reason: string | null

  follow_up_required: boolean
  follow_up_notes: string | null

  created_at: string
}
