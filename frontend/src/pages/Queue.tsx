import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { getQueueItems, dispatchNext } from "../api/queue"
import { getPatients } from "../api/patients"
import { getCampaigns } from "../api/campaigns"

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

function getDeadlineStatus(deadline: string | null) {
  if (!deadline) {
    return {
      text: "No deadline",
      className: "text-slate-400",
    }
  }

  const deadlineTime = new Date(deadline).getTime()
  const now = Date.now()

  const hoursRemaining = (deadlineTime - now) / (1000 * 60 * 60)

  if (hoursRemaining <= 0) {
    return {
      text: "Overdue",
      className: "text-red-600 font-semibold",
    }
  }

  if (hoursRemaining <= 6) {
    return {
      text: `${Math.ceil(hoursRemaining)}h left`,
      className: "text-red-600 font-semibold",
    }
  }

  if (hoursRemaining <= 24) {
    return {
      text: `${Math.ceil(hoursRemaining)}h left`,
      className: "text-orange-600 font-medium",
    }
  }

  return {
    text: `${Math.ceil(hoursRemaining / 24)}d left`,
    className: "text-green-600",
  }
}

export default function Queue() {
  const navigate = useNavigate()
  const [items, setItems] = useState<QueueItem[]>([])
  const [patients, setPatients] = useState<Patient[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const [workerId, setWorkerId] = useState("frontend-worker-01")
  const [dispatching, setDispatching] = useState(false)
  const [dispatchMessage, setDispatchMessage] = useState("")

  useEffect(() => {
    let active = true

    async function loadQueue() {
      try {
        const [queueData, patientData, campaignData] = await Promise.all([
          getQueueItems(),
          getPatients(),
          getCampaigns(),
        ])

        if (active) {
          setItems(queueData)
          setPatients(patientData)
          setCampaigns(campaignData)
          setLoading(false)
        }
      } catch (err) {
        console.error(err)
        if (active) {
          setError("Failed to load queue")
          setLoading(false)
        }
      }
    }

    loadQueue()

    const interval = setInterval(loadQueue, 10000)

    return () => {
      active = false
      clearInterval(interval)
    }
  }, [])

  async function handleDispatch() {
    try {
      setDispatching(true)
      setDispatchMessage("")

      const result = await dispatchNext(workerId)

      if (result.reserved && result.queue_item_id) {
        setDispatchMessage(
          `Queue item #${result.queue_item_id} dispatched successfully.`
        )
      } else {
        setDispatchMessage(
          result.reason || "No callable queue item available or outbound capacity is full."
        )
      }

      const updatedItems = await getQueueItems()
      setItems(updatedItems)
    } catch (err: any) {
      console.error(err)

      const message =
        err?.response?.data?.detail || "No queue item could be dispatched."

      setDispatchMessage(message)
    } finally {
      setDispatching(false)
    }
  }

  function getPatientName(patientId: number) {
    const patient = patients.find((item) => item.id === patientId)

    if (!patient) {
      return `Patient #${patientId}`
    }

    return `${patient.first_name} ${patient.last_name}`
  }

  function getCampaignName(campaignId: number) {
    const campaign = campaigns.find((item) => item.id === campaignId)

    if (!campaign) {
      return `Campaign #${campaignId}`
    }

    return campaign.name
  }

  const total = items.length

  const pending = items.filter((item) => item.status === "PENDING").length

  const calling = items.filter(
    (item) => item.status === "CALLING" || item.status === "CONNECTED"
  ).length

  const completed = items.filter((item) => item.status === "COMPLETED").length

  const escalated = items.filter((item) => item.status === "ESCALATED").length

  const retryScheduled = items.filter(
    (item) => item.status === "RETRY_SCHEDULED"
  ).length

  const callbackScheduled = items.filter(
    (item) => item.status === "CALLBACK_SCHEDULED"
  ).length

  const failed = items.filter((item) => item.status === "FAILED").length

  const overdue = items.filter((item) => {
    if (!item.deadline_at) return false
    return new Date(item.deadline_at).getTime() <= Date.now()
  }).length

  if (loading) {
    return (
      <div className="p-8">
        <p className="text-slate-500">Loading queue...</p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Outreach Queue
          </h1>

          <p className="mt-1 text-slate-500">
            Monitor and manage patient outreach work.
          </p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            value={workerId}
            onChange={(event) => setWorkerId(event.target.value)}
            placeholder="Worker ID"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
          />

          <button
            onClick={handleDispatch}
            disabled={dispatching || !workerId.trim()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {dispatching ? "Dispatching..." : "Dispatch Next"}
          </button>
        </div>
      </div>

      {/* Dispatch Message */}
      {dispatchMessage && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700">
          {dispatchMessage}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Total Queue</p>

          <p className="mt-2 text-3xl font-bold text-slate-900">{total}</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Pending</p>

          <p className="mt-2 text-3xl font-bold text-yellow-600">{pending}</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Active Calls</p>

          <p className="mt-2 text-3xl font-bold text-blue-600">{calling}</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Completed</p>

          <p className="mt-2 text-3xl font-bold text-green-600">{completed}</p>
        </div>
      </div>

      {/* Operational Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Escalated</p>

          <p className="mt-2 text-2xl font-bold text-red-600">{escalated}</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Retry Scheduled</p>

          <p className="mt-2 text-2xl font-bold text-yellow-600">
            {retryScheduled}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Callbacks</p>

          <p className="mt-2 text-2xl font-bold text-purple-600">
            {callbackScheduled}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Overdue</p>

          <p className="mt-2 text-2xl font-bold text-red-600">{overdue}</p>
        </div>
      </div>

      {/* Queue Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div>
            <h2 className="font-semibold text-slate-900">Queue Items</h2>

            <p className="text-sm text-slate-500">
              {failed} failed item{failed !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-left">Queue ID</th>
                <th className="px-4 py-3 text-left">Patient</th>
                <th className="px-4 py-3 text-left">Campaign</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Priority</th>
                <th className="px-4 py-3 text-left">Attempts</th>
                <th className="px-4 py-3 text-left">Deadline</th>
              </tr>
            </thead>

            <tbody>
              {items.map((item) => {
                const deadline = getDeadlineStatus(item.deadline_at)

                return (
                  <tr
                    key={item.id}
                    onClick={() => navigate(`/queue/${item.id}`)}
                    className="cursor-pointer border-b border-slate-100 hover:bg-slate-50"
                  >
                    <td className="px-4 py-4 font-medium">#{item.id}</td>

                    <td className="px-4 py-4">
                      <div>
                        <p className="font-medium text-slate-900">
                          {getPatientName(item.patient_id)}
                        </p>

                        <p className="text-xs text-slate-400">
                          ID: {item.patient_id}
                        </p>
                      </div>
                    </td>

                    <td className="px-4 py-4">
                      <div>
                        <p className="font-medium text-slate-900">
                          {getCampaignName(item.campaign_id)}
                        </p>

                        <p className="text-xs text-slate-400">
                          ID: {item.campaign_id}
                        </p>
                      </div>
                    </td>

                    <td className="px-4 py-4">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${statusClass(
                          item.status
                        )}`}
                      >
                        {item.status}
                      </span>
                    </td>

                    <td className="px-4 py-4">
                      <span className="font-semibold">
                        {item.priority_score}
                      </span>
                    </td>

                    <td className="px-4 py-4">{item.attempt_count}</td>

                    <td className="px-4 py-4">
                      <div className="text-xs">
                        <div className={deadline.className}>
                          {deadline.text}
                        </div>

                        {item.deadline_at && (
                          <div className="mt-1 text-slate-400">
                            {new Date(item.deadline_at).toLocaleString()}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {items.length === 0 && (
          <div className="p-8 text-center text-slate-500">
            No queue items found.
          </div>
        )}
      </div>
    </div>
  )
}
