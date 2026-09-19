export interface VoiceIntakeExtraction {
  symptoms: string[]
  red_flags: string[]
  medication_concerns: string[]
  patient_questions: string[]
  consent_confirmed: boolean
  identity_verified: boolean
}

export interface TriageResult {
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string
  evidence: string[]
  red_flags: string[]
  recommended_action: string
  confidence: number
}

export interface TriagePipelineResponse {
  call_id?: number
  patient_id?: number
  intake: VoiceIntakeExtraction | null
  triage: TriageResult
  assessment_id: number
  existing?: boolean
}

export interface EscalationAssessment {
  assessor_name: string
  risk_level: string
  recommended_action: string
  rationale: string
  evidence: string[]
  red_flags: string[]
  confidence: number
}

export interface ConsensusResult {
  final_risk_level: string
  final_action: string
  consensus_confidence: number
  disagreement: boolean
  disagreement_reasons: string[]
  red_flag_override: boolean
  red_flags_triggered: string[]
  evidence_summary: string[]
}

export interface ConsensusResponse {
  existing: boolean
  consensus: {
    id: number
    hospital_id: number
    patient_id: number
    call_id: number
    queue_item_id: number
    assessment_a: EscalationAssessment | string
    assessment_b: EscalationAssessment | string
    final_risk_level: string
    final_action: string
    disagreement: boolean
    disagreement_reasons: string[] | string
    red_flag_override: boolean
    red_flags: string[] | string
    evidence: string[] | string
    consensus_confidence: number
    created_at: string
  }
}
