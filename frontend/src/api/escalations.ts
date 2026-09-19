import apiClient from "./client"
import type { Escalation } from "../types/escalation"
import { MOCK_ESCALATIONS } from "../mock/mockData"

let escalationsStore = [...MOCK_ESCALATIONS]

export async function getEscalations(): Promise<Escalation[]> {
  try {
    const response = await apiClient.get("/escalations")
    const data = response.data || []
    if (data.length > 0) return data
    return escalationsStore
  } catch {
    return escalationsStore
  }
}

export async function getEscalation(
  escalationId: number
): Promise<Escalation> {
  try {
    const response = await apiClient.get(
      `/escalations/${escalationId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  const found = escalationsStore.find((e) => e.id === Number(escalationId))
  if (found) return found

  return {
    id: escalationId,
    hospital_id: 101,
    patient_id: 1,
    queue_item_id: 101,
    call_id: 501,
    consensus_assessment_id: 301,
    reason: "Clinical triage flag requiring clinician review",
    priority: "HIGH",
    evidence: JSON.stringify(["Patient reported persistent symptom flag"]),
    status: "OPEN",
    source: "AI_TRIAGE_WORKFLOW",
    final_action: "CLINICIAN_CALLBACK_REQUIRED",
    resolved_at: null,
    resolution_notes: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
}

export async function getCallEscalation(
  callId: number
): Promise<Escalation | null> {
  try {
    const response = await apiClient.get(
      `/escalations/call/${callId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  const found = escalationsStore.find((e) => e.call_id === Number(callId))
  if (found) return found

  return null
}

export async function updateEscalationStatus(
  escalationId: number,
  status: string,
  resolution_notes?: string
): Promise<Escalation> {
  try {
    const response = await apiClient.patch(
      `/escalations/${escalationId}/status`,
      {
        status,
        resolution_notes,
      }
    )
    return response.data
  } catch {
    const index = escalationsStore.findIndex((e) => e.id === Number(escalationId))
    if (index !== -1) {
      escalationsStore[index] = {
        ...escalationsStore[index],
        status,
        resolution_notes: resolution_notes || escalationsStore[index].resolution_notes,
        resolved_at: status === "RESOLVED" ? new Date().toISOString() : escalationsStore[index].resolved_at,
        updated_at: new Date().toISOString(),
      }
      return escalationsStore[index]
    }

    return {
      id: escalationId,
      hospital_id: 101,
      patient_id: 1,
      queue_item_id: null,
      call_id: null,
      consensus_assessment_id: null,
      reason: "Updated escalation",
      priority: "HIGH",
      evidence: null,
      status,
      source: "MANUAL",
      final_action: null,
      resolved_at: status === "RESOLVED" ? new Date().toISOString() : null,
      resolution_notes: resolution_notes || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
  }
}
