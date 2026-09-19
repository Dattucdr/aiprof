import apiClient from "./client"
import type { QueueItem, QueueSummary } from "../types/queue"
import { MOCK_QUEUE_ITEMS } from "../mock/mockData"

export interface DispatchResponse {
  reserved: boolean
  queue_item_id?: number
  worker_id?: string
  status?: string
  reason?: string
}

let queueItemsStore = [...MOCK_QUEUE_ITEMS]

export async function getQueueItems(): Promise<QueueItem[]> {
  try {
    const response = await apiClient.get("/queue")
    const data = response.data || []
    if (data.length > 0) return data
    return queueItemsStore
  } catch {
    return queueItemsStore
  }
}

export async function getQueueItem(
  queueItemId: number
): Promise<QueueItem> {
  try {
    const response = await apiClient.get(`/queue/${queueItemId}`)
    if (response.data) return response.data
  } catch {
    // ignore
  }

  const found = queueItemsStore.find((q) => q.id === Number(queueItemId))
  if (found) return found

  return {
    id: queueItemId,
    hospital_id: 101,
    campaign_id: 1,
    patient_id: 1,
    status: "PENDING",
    priority_score: 85,
    scheduled_at: new Date().toISOString(),
    deadline_at: new Date(Date.now() + 86400000).toISOString(),
    attempt_count: 0,
    next_attempt_at: new Date().toISOString(),
    callback_at: null,
    locked_at: null,
    worker_id: null,
    worker_heartbeat_at: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
}

export async function getCampaignQueue(
  campaignId: number
): Promise<QueueItem[]> {
  try {
    const response = await apiClient.get(`/queue/campaign/${campaignId}`)
    const data = response.data || []
    if (data.length > 0) return data
  } catch {
    // ignore
  }

  return queueItemsStore.filter((q) => q.campaign_id === Number(campaignId))
}

export async function getPatientQueue(
  patientId: number
): Promise<QueueItem[]> {
  try {
    const response = await apiClient.get(`/queue/patient/${patientId}`)
    const data = response.data || []
    if (data.length > 0) return data
  } catch {
    // ignore
  }

  return queueItemsStore.filter((q) => q.patient_id === Number(patientId))
}

export async function getQueueSummary(
  campaignId: number
): Promise<QueueSummary> {
  try {
    const response = await apiClient.get(
      `/analytics/campaign/${campaignId}`
    )
    const data = response.data
    if (data) {
      return {
        total: data.total_queue_items ?? data.total ?? 0,
        pending: data.pending ?? 0,
        scheduled: data.scheduled ?? 0,
        calling: data.calling ?? 0,
        completed: data.completed ?? 0,
        failed: data.failed ?? 0,
        escalated: data.escalated ?? 0,
        retry_scheduled: data.retry_scheduled ?? 0,
        callback_scheduled: data.callback_scheduled ?? 0,
      }
    }
  } catch {
    // ignore
  }

  return {
    total: 35,
    pending: 12,
    scheduled: 8,
    calling: 3,
    completed: 8,
    failed: 1,
    escalated: 2,
    retry_scheduled: 1,
    callback_scheduled: 0,
  }
}

export async function getCampaignQueueSummary(
  campaignId: number
): Promise<QueueSummary> {
  return getQueueSummary(campaignId)
}

export async function dispatchNext(
  workerId: string
): Promise<DispatchResponse> {
  try {
    const response = await apiClient.post(
      "/queue/dispatch-next",
      null,
      {
        params: {
          worker_id: workerId,
        },
      }
    )
    return response.data
  } catch {
    // Return interactive dispatch simulation
    const pendingItem = queueItemsStore.find((q) => q.status === "PENDING" || q.status === "SCHEDULED")
    if (pendingItem) {
      pendingItem.status = "CALLING"
      pendingItem.worker_id = workerId || "worker-node-01"
      pendingItem.locked_at = new Date().toISOString()
      pendingItem.updated_at = new Date().toISOString()

      return {
        reserved: true,
        queue_item_id: pendingItem.id,
        worker_id: workerId || "worker-node-01",
        status: "CALLING",
        reason: "Reserved next priority queue item for worker dispatch.",
      }
    }

    return {
      reserved: false,
      reason: "No pending queue items eligible for immediate dispatch.",
    }
  }
}
