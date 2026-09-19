export interface EscalationAssessment {
  id?: number
  assessor: string
  risk_level: string
  recommended_action: string
  evidence: string[]
  red_flags: string[]
  confidence: number
}

export interface ConsensusResult {
  assessments: EscalationAssessment[]
  consensus_reached: boolean
  final_risk_level: string
  final_action: string
  disagreement: boolean
  disagreement_reason: string | null
  evidence: string[]
  red_flags: string[]
}

export interface ConsensusAssessment {
  id: number
  hospital_id: number
  patient_id: number
  call_id: number
  queue_item_id: number | null

  assessment_a: string | EscalationAssessment
  assessment_b: string | EscalationAssessment

  consensus_reached: boolean
  disagreement: boolean
  disagreement_reason: string | null

  final_risk_level: string
  final_action: string

  evidence: string | string[]
  red_flags: string | string[]

  created_at: string
}
