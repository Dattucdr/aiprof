import apiClient from "./client"
import { MOCK_CALLS } from "../mock/mockData"

export interface Call {
  id: number
  hospital_id: number
  campaign_id: number
  patient_id: number
  queue_item_id: number
  attempt_number: number
  idempotency_key: string
  status: string
  outcome: string | null
  worker_id: string | null
  started_at: string | null
  connected_at: string | null
  ended_at: string | null
  duration_seconds: number | null
  transcript: string | null
  notes: string | null
  failure_reason: string | null
  created_at: string
}

let callsStore = [...MOCK_CALLS]

export async function getQueueCalls(
  queueItemId: number
): Promise<Call[]> {
  try {
    const response = await apiClient.get(
      `/calls/queue/${queueItemId}`
    )
    const data = response.data || []
    if (data.length > 0) return data
  } catch {
    // ignore
  }

  return callsStore.filter((c) => c.queue_item_id === Number(queueItemId))
}

export async function getPatientCalls(
  patientId: number
): Promise<Call[]> {
  try {
    const response = await apiClient.get(
      `/calls/patient/${patientId}`
    )
    const data = response.data || []
    if (data.length > 0) return data
  } catch {
    // ignore
  }

  return callsStore.filter((c) => c.patient_id === Number(patientId))
}

export async function getCall(
  callId: number
): Promise<Call> {
  try {
    const response = await apiClient.get(
      `/calls/${callId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  const found = callsStore.find((c) => c.id === Number(callId))
  if (found) return found

  return {
    id: callId,
    hospital_id: 101,
    campaign_id: 1,
    patient_id: 1,
    queue_item_id: 101,
    attempt_number: 1,
    idempotency_key: `call-key-${callId}`,
    status: "COMPLETED",
    outcome: "SUCCESSFUL",
    worker_id: "worker-node-01",
    started_at: new Date(Date.now() - 300000).toISOString(),
    connected_at: new Date(Date.now() - 290000).toISOString(),
    ended_at: new Date(Date.now() - 60000).toISOString(),
    duration_seconds: 230,
    transcript: "AI Agent: Good day! This is your healthcare check-in assistant. How are you feeling after your recent appointment?\n\nPatient: I'm feeling well, thank you!",
    notes: "Patient reported good progress and confirmed medication adherence.",
    failure_reason: null,
    created_at: new Date(Date.now() - 300000).toISOString(),
  }
}
