import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import { getQueueItem } from "../api/queue"
import { getPatient } from "../api/patients"
import { getCampaign } from "../api/campaigns"
import { getQueueCalls, Call } from "../api/calls"

import type { QueueItem } from "../types/queue"
import type { Patient } from "../types/patient"
import type { Campaign } from "../types/campaign"

function statusClass(status: string) {
  switch (status) {
    case "COMPLETED":
      return "bg-green-100 text-green-700"

    case "CALLING":
    case "CONNECTED":
      return "bg-blue-100 text-blue-700"

    case "ESCALATED":
      return "bg-red-100 text-red-700"

    case "FAILED":
      return "bg-gray-100 text-gray-700"

    case "RETRY_SCHEDULED":
      return "bg-yellow-100 text-yellow-700"

    case "CALLBACK_SCHEDULED":
      return "bg-purple-100 text-purple-700"

    default:
      return "bg-slate-100 text-slate-700"
  }
}

function formatDate(value: string | null) {
  if (!value) {
    return "—"
  }

  return new Date(value).toLocaleString()
}

export default function QueueDetails() {
  const { queueItemId } = useParams()
  const navigate = useNavigate()

  const [queueItem, setQueueItem] = useState<QueueItem | null>(null)
  const [patient, setPatient] = useState<Patient | null>(null)
  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [calls, setCalls] = useState<Call[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function loadData() {
      if (!queueItemId) {
        return
      }

      try {
        setLoading(true)

        const queueData = await getQueueItem(Number(queueItemId))
        setQueueItem(queueData)

        const [patientData, campaignData, callData] = await Promise.all([
          getPatient(queueData.patient_id),
          getCampaign(queueData.campaign_id),
          getQueueCalls(queueData.id),
        ])

        setPatient(patientData)
        setCampaign(campaignData)
        setCalls(callData)
      } catch (err) {
        console.error(err)
        setError("Failed to load queue item")
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [queueItemId])

  if (loading) {
    return (
      <div className="p-8">
        <p className="text-slate-500">Loading queue item...</p>
      </div>
    )
  }

  if (error || !queueItem) {
    return (
      <div className="p-8 space-y-4">
        <button
          onClick={() => navigate("/queue")}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to Queue
        </button>

        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error || "Queue item not found"}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={() => navigate("/queue")}
            className="mb-3 text-sm text-blue-600 hover:underline"
          >
            ← Back to Queue
          </button>

          <h1 className="text-3xl font-bold text-slate-900">
            Queue Item #{queueItem.id}
          </h1>

          <p className="mt-1 text-slate-500">
            Outreach queue details and operational state
          </p>
        </div>

        <span
          className={`rounded-full px-4 py-2 text-sm font-medium ${statusClass(
            queueItem.status
          )}`}
        >
          {queueItem.status}
        </span>
      </div>

      {/* Patient + Campaign */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Patient</h2>

          <div className="mt-4 space-y-3">
            <div>
              <p className="text-xs text-slate-400">Name</p>

              <p className="font-medium text-slate-900">
                {patient
                  ? `${patient.first_name} ${patient.last_name}`
                  : `Patient #${queueItem.patient_id}`}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-400">MRN</p>

              <p className="text-slate-700">{patient?.mrn || "—"}</p>
            </div>

            <div>
              <p className="text-xs text-slate-400">Phone</p>

              <p className="text-slate-700">{patient?.phone || "—"}</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Campaign</h2>

          <div className="mt-4 space-y-3">
            <div>
              <p className="text-xs text-slate-400">Name</p>

              <p className="font-medium text-slate-900">
                {campaign?.name || `Campaign #${queueItem.campaign_id}`}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-400">Status</p>

              <p className="text-slate-700">{campaign?.status || "—"}</p>
            </div>

            <div>
              <p className="text-xs text-slate-400">Follow-up Window</p>

              <p className="text-slate-700">
                {campaign ? `${campaign.follow_up_window_days} days` : "—"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Queue Information */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">
          Queue Information
        </h2>

        <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
          <div>
            <p className="text-xs text-slate-400">Priority Score</p>

            <p className="mt-1 text-2xl font-bold text-slate-900">
              {queueItem.priority_score}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Attempts</p>

            <p className="mt-1 text-2xl font-bold text-slate-900">
              {queueItem.attempt_count}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Call Attempts</p>

            <p className="mt-1 text-2xl font-bold text-slate-900">
              {calls.length}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Scheduled</p>

            <p className="mt-1 text-sm text-slate-700">
              {formatDate(queueItem.scheduled_at)}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Deadline</p>

            <p className="mt-1 text-sm text-slate-700">
              {formatDate(queueItem.deadline_at)}
            </p>
          </div>
        </div>
      </div>

      {/* Retry / Callback */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">
            Retry Information
          </h2>

          <div className="mt-4 space-y-3">
            <div>
              <p className="text-xs text-slate-400">Next Attempt</p>

              <p className="text-slate-700">
                {formatDate(queueItem.next_attempt_at)}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-400">Attempts Made</p>

              <p className="text-slate-700">{queueItem.attempt_count}</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Callback</h2>

          <div className="mt-4">
            <p className="text-xs text-slate-400">Callback Time</p>

            <p className="mt-1 text-slate-700">
              {formatDate(queueItem.callback_at)}
            </p>
          </div>
        </div>
      </div>

      {/* Worker Information */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">
          Worker / Lock Information
        </h2>

        <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div>
            <p className="text-xs text-slate-400">Worker ID</p>

            <p className="mt-1 font-mono text-sm text-slate-700">
              {queueItem.worker_id || "Not assigned"}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Locked At</p>

            <p className="mt-1 text-sm text-slate-700">
              {formatDate(queueItem.locked_at)}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">Last Heartbeat</p>

            <p className="mt-1 text-sm text-slate-700">
              {formatDate(queueItem.worker_heartbeat_at)}
            </p>
          </div>
        </div>
      </div>

      {/* Call History */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-5">
          <h2 className="text-lg font-semibold text-slate-900">Call History</h2>

          <p className="mt-1 text-sm text-slate-500">
            {calls.length} outreach attempt{calls.length !== 1 ? "s" : ""}
          </p>
        </div>

        <div className="divide-y divide-slate-100">
          {calls.map((call) => (
            <div
              key={call.id}
              onClick={() => navigate(`/calls/${call.id}`)}
              className="cursor-pointer p-6 hover:bg-slate-50"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-slate-900">
                      Attempt #{call.attempt_number}
                    </h3>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {call.status}
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-slate-500">
                    Started: {formatDate(call.started_at)}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-sm font-medium text-slate-700">
                    {call.outcome || "No outcome"}
                  </p>

                  {call.duration_seconds !== null && (
                    <p className="mt-1 text-xs text-slate-400">
                      {call.duration_seconds}s
                    </p>
                  )}
                </div>
              </div>

              {call.worker_id && (
                <div className="mt-4 text-xs text-slate-400">
                  Worker: {call.worker_id}
                </div>
              )}

              {call.notes && (
                <div className="mt-4 rounded-lg bg-slate-50 p-4">
                  <p className="text-xs font-medium text-slate-500">Notes</p>

                  <p className="mt-1 text-sm text-slate-700">{call.notes}</p>
                </div>
              )}

              {call.failure_reason && (
                <div className="mt-4 rounded-lg border border-red-100 bg-red-50 p-4">
                  <p className="text-xs font-medium text-red-600">
                    Failure Reason
                  </p>

                  <p className="mt-1 text-sm text-red-700">
                    {call.failure_reason}
                  </p>
                </div>
              )}
            </div>
          ))}

          {calls.length === 0 && (
            <div className="p-8 text-center text-sm text-slate-500">
              No calls have been made for this queue item yet.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
