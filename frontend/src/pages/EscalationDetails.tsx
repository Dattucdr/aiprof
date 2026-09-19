import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import {
  getEscalation,
  updateEscalationStatus,
} from "../api/escalations"

import type { Escalation } from "../types/escalation"

export default function EscalationDetails() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [escalation, setEscalation] =
    useState<Escalation | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const [resolutionNotes, setResolutionNotes] =
    useState("")

  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (id) {
      loadEscalation(Number(id))
    }
  }, [id])

  async function loadEscalation(escalationId: number) {
    try {
      setLoading(true)
      setError("")

      const data = await getEscalation(escalationId)

      setEscalation(data)
      setResolutionNotes(data.resolution_notes ?? "")
    } catch (err) {
      console.error(err)
      setError("Failed to load escalation")
    } finally {
      setLoading(false)
    }
  }

  async function changeStatus(status: string) {
    if (!escalation) return

    try {
      setUpdating(true)
      setError("")

      const updated = await updateEscalationStatus(
        escalation.id,
        status,
        resolutionNotes
      )

      setEscalation(updated)
    } catch (err) {
      console.error(err)
      setError("Failed to update escalation")
    } finally {
      setUpdating(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        Loading escalation...
      </div>
    )
  }

  if (!escalation) {
    return (
      <div className="p-6">
        <p className="text-red-600">
          Escalation not found.
        </p>

        <button
          onClick={() => navigate("/escalations")}
          className="mt-4 rounded-lg border px-4 py-2"
        >
          Back to Escalations
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">

      {/* Header */}

      <div className="flex items-center justify-between">

        <div>
          <button
            onClick={() => navigate("/escalations")}
            className="mb-3 text-sm text-gray-500 hover:text-gray-900"
          >
            ← Back to Escalations
          </button>

          <h1 className="text-2xl font-bold">
            Escalation #{escalation.id}
          </h1>

          <p className="mt-1 text-gray-500">
            Patient #{escalation.patient_id}
          </p>
        </div>

        <div className="text-right">
          <p className="text-sm text-gray-500">
            Priority
          </p>

          <p className="text-xl font-bold">
            {escalation.priority}
          </p>
        </div>

      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Status */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Escalation Status
        </h2>

        <div className="mt-4 flex flex-wrap gap-3">

          <span className="rounded-full border px-4 py-2">
            Current: {escalation.status}
          </span>

          {escalation.status === "OPEN" && (
            <button
              disabled={updating}
              onClick={() =>
                changeStatus("IN_REVIEW")
              }
              className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
            >
              Start Review
            </button>
          )}

          {escalation.status === "IN_REVIEW" && (
            <>
              <button
                disabled={updating}
                onClick={() =>
                  changeStatus("RESOLVED")
                }
                className="rounded-lg bg-black px-4 py-2 text-white disabled:opacity-50"
              >
                Resolve
              </button>

              <button
                disabled={updating}
                onClick={() =>
                  changeStatus("CLOSED")
                }
                className="rounded-lg border px-4 py-2 disabled:opacity-50"
              >
                Close
              </button>
            </>
          )}

        </div>

      </div>

      {/* Core Information */}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold">
            Escalation Information
          </h2>

          <div className="mt-4 space-y-3 text-sm">

            <div>
              <span className="font-medium">
                Patient:
              </span>{" "}
              #{escalation.patient_id}
            </div>

            <div>
              <span className="font-medium">
                Call:
              </span>{" "}
              {escalation.call_id
                ? `#${escalation.call_id}`
                : "-"}
            </div>

            <div>
              <span className="font-medium">
                Queue Item:
              </span>{" "}
              {escalation.queue_item_id
                ? `#${escalation.queue_item_id}`
                : "-"}
            </div>

            <div>
              <span className="font-medium">
                Source:
              </span>{" "}
              {escalation.source}
            </div>

            <div>
              <span className="font-medium">
                Final Action:
              </span>{" "}
              {escalation.final_action ?? "-"}
            </div>

            <div>
              <span className="font-medium">
                Created:
              </span>{" "}
              {new Date(
                escalation.created_at
              ).toLocaleString()}
            </div>

            <div>
              <span className="font-medium">
                Resolved:
              </span>{" "}
              {escalation.resolved_at
                ? new Date(
                    escalation.resolved_at
                  ).toLocaleString()
                : "-"}
            </div>

          </div>

        </div>

        {/* Reason */}

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold">
            Reason
          </h2>

          <p className="mt-4 whitespace-pre-wrap text-sm text-gray-700">
            {escalation.reason}
          </p>

        </div>

      </div>

      {/* Evidence */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Evidence
        </h2>

        <div className="mt-4 whitespace-pre-wrap rounded-lg bg-gray-50 p-4 text-sm">
          {typeof escalation.evidence === "string"
            ? escalation.evidence
            : JSON.stringify(escalation.evidence, null, 2) || "No evidence recorded."}
        </div>

      </div>

      {/* Resolution */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Clinical Review / Resolution
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Add notes explaining the outcome of the review.
        </p>

        <textarea
          value={resolutionNotes}
          onChange={(e) =>
            setResolutionNotes(e.target.value)
          }
          rows={5}
          placeholder="Enter resolution notes..."
          className="mt-4 w-full rounded-lg border p-3 outline-none focus:ring-2"
          disabled={
            escalation.status === "CLOSED"
          }
        />

        {escalation.resolution_notes && (
          <div className="mt-4 rounded-lg bg-gray-50 p-4">

            <p className="text-sm font-medium">
              Saved Resolution Notes
            </p>

            <p className="mt-2 whitespace-pre-wrap text-sm text-gray-700">
              {escalation.resolution_notes}
            </p>

          </div>
        )}

      </div>

    </div>
  )
}
