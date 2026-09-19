import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import apiClient from "../api/client"
import type { Call } from "../api/calls"

function statusClass(status: string) {
  switch (status) {
    case "COMPLETED":
      return "bg-green-100 text-green-700"

    case "IN_PROGRESS":
      return "bg-blue-100 text-blue-700"

    case "FAILED":
      return "bg-red-100 text-red-700"

    default:
      return "bg-slate-100 text-slate-700"
  }
}

export default function Calls() {
  const navigate = useNavigate()

  const [calls, setCalls] = useState<Call[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function loadCalls() {
      try {
        setLoading(true)

        /*
         * Use the actual backend endpoint that returns
         * tenant-scoped calls.
         */
        const response = await apiClient.get("/calls")

        setCalls(response.data || [])
      } catch (err) {
        console.error(err)
        setError("Failed to load calls")
      } finally {
        setLoading(false)
      }
    }

    loadCalls()
  }, [])

  const completed = calls.filter(
    (call) => call.status === "COMPLETED"
  ).length

  const inProgress = calls.filter(
    (call) => call.status === "IN_PROGRESS"
  ).length

  const failed = calls.filter(
    (call) => call.status === "FAILED"
  ).length

  const connected = calls.filter(
    (call) => call.outcome === "CONNECTED"
  ).length

  if (loading) {
    return (
      <div className="p-8">
        <p className="text-slate-500">
          Loading calls...
        </p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">

      {/* Header */}

      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Calls
        </h1>

        <p className="mt-1 text-slate-500">
          Monitor patient outreach calls and processing.
        </p>
      </div>

      {/* Error */}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Summary */}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Total Calls
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-900">
            {calls.length}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            In Progress
          </p>

          <p className="mt-2 text-3xl font-bold text-blue-600">
            {inProgress}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Connected
          </p>

          <p className="mt-2 text-3xl font-bold text-green-600">
            {connected}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Failed
          </p>

          <p className="mt-2 text-3xl font-bold text-red-600">
            {failed}
          </p>
        </div>

      </div>

      {/* Call table */}

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

        <div className="border-b border-slate-200 px-5 py-4">

          <h2 className="font-semibold text-slate-900">
            Outreach Calls
          </h2>

          <p className="text-sm text-slate-500">
            Select a call to view its complete processing history.
          </p>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full text-sm">

            <thead className="bg-slate-50 border-b border-slate-200">

              <tr>

                <th className="px-4 py-3 text-left">
                  Call
                </th>

                <th className="px-4 py-3 text-left">
                  Patient
                </th>

                <th className="px-4 py-3 text-left">
                  Campaign
                </th>

                <th className="px-4 py-3 text-left">
                  Attempt
                </th>

                <th className="px-4 py-3 text-left">
                  Status
                </th>

                <th className="px-4 py-3 text-left">
                  Outcome
                </th>

                <th className="px-4 py-3 text-left">
                  Started
                </th>

              </tr>

            </thead>

            <tbody>

              {calls.map((call) => (

                <tr
                  key={call.id}
                  onClick={() =>
                    navigate(`/calls/${call.id}`)
                  }
                  className="cursor-pointer border-b border-slate-100 hover:bg-slate-50"
                >

                  <td className="px-4 py-4 font-medium">
                    #{call.id}
                  </td>

                  <td className="px-4 py-4">
                    Patient #{call.patient_id}
                  </td>

                  <td className="px-4 py-4">
                    Campaign #{call.campaign_id}
                  </td>

                  <td className="px-4 py-4">
                    #{call.attempt_number}
                  </td>

                  <td className="px-4 py-4">

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${statusClass(
                        call.status
                      )}`}
                    >
                      {call.status}
                    </span>

                  </td>

                  <td className="px-4 py-4">
                    {call.outcome || "—"}
                  </td>

                  <td className="px-4 py-4 text-slate-500">
                    {call.started_at
                      ? new Date(
                          call.started_at
                        ).toLocaleString()
                      : "—"}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

        {calls.length === 0 && (
          <div className="p-8 text-center text-slate-500">
            No calls found.
          </div>
        )}

      </div>

    </div>
  )
}
