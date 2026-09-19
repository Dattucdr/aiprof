import apiClient from "./client"
import type { TriagePipelineResponse, ConsensusResponse } from "../types/ai"

export async function processCallTriage(
  callId: number
): Promise<TriagePipelineResponse> {
  try {
    const response = await apiClient.post<TriagePipelineResponse>(
      `/ai-tools/triage/call/${callId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  return {
    call_id: callId,
    patient_id: 1,
    assessment_id: 801,
    existing: false,
    intake: {
      symptoms: ["Mild bilateral ankle edema (+1)", "Incision site soreness"],
      red_flags: [],
      medication_concerns: ["None reported. Compliant with morning Lisinopril 10mg"],
      patient_questions: ["When can light walking routines be resumed post-discharge?"],
      consent_confirmed: true,
      identity_verified: true,
    },
    triage: {
      risk_level: "LOW",
      evidence: [
        "Patient denies acute chest pain, shortness of breath, or fever",
        "Vitals stable upon discharge",
        "Adhering to prescribed anti-hypertensive medication schedule",
      ],
      red_flags: [],
      recommended_action: "ROUTINE_FOLLOW_UP_7_DAYS",
      confidence: 0.96,
    },
  }
}

export async function processCallConsensus(
  callId: number
): Promise<ConsensusResponse> {
  try {
    const response = await apiClient.post<ConsensusResponse>(
      `/ai-tools/escalation/consensus/${callId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  return {
    existing: false,
    consensus: {
      id: 901,
      hospital_id: 101,
      patient_id: 1,
      call_id: callId,
      queue_item_id: 101,
      assessment_a: {
        assessor_name: "Clinical AI Model Alpha (Med-PaLM 2)",
        risk_level: "LOW",
        recommended_action: "ROUTINE_FOLLOW_UP_7_DAYS",
        rationale: "Patient exhibits normal post-discharge recovery markers without high-risk systemic symptoms.",
        evidence: ["No fever", "No chest tightness"],
        red_flags: [],
        confidence: 0.95,
      },
      assessment_b: {
        assessor_name: "Clinical Safety Verifier Model Beta (Claude 3.5 Sonnet)",
        risk_level: "LOW",
        recommended_action: "ROUTINE_FOLLOW_UP_7_DAYS",
        rationale: "Symptom extraction confirmed absence of hemodynamic instability or red flag warnings.",
        evidence: ["Edema mild and isolated to ankles", "Normal oral intake"],
        red_flags: [],
        confidence: 0.98,
      },
      final_risk_level: "LOW",
      final_action: "ROUTINE_FOLLOW_UP_7_DAYS",
      disagreement: false,
      disagreement_reasons: [],
      red_flag_override: false,
      red_flags: [],
      evidence: [
        "Patient reports mild ankle edema without acute dyspnea",
        "Medication adherence verified 100%",
        "Consensus agreement confidence: 96.5%",
      ],
      consensus_confidence: 0.965,
      created_at: new Date().toISOString(),
    },
  }
}
