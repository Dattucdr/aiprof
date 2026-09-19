import { useState } from "react"
import { getPatientAudit } from "../api/audit"
import type { AuditLog } from "../types/audit"

function formatDetails(value: string) {
  try {
    return JSON.stringify(
      JSON.parse(value),
      null,
      2
    )
  } catch {
    return value
  }
}

export default function Audit() {
  const [patientId, setPatientId] = useState("")
  const [logs, setLogs] = useState<AuditLog[]>([])

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function loadAudit() {
    if (!patientId) {
      setError("Enter a patient ID")
      return
    }

    try {
      setLoading(true)
      setError("")

      const data = await getPatientAudit(
        Number(patientId)
      )

      setLogs(data)
    } catch (err) {
      console.error(err)
      setError("Failed to load audit logs")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 p-6">

      <div>
        <h1 className="text-2xl font-bold">
          Audit Trail
        </h1>

        <p className="mt-1 text-gray-500">
          Trace AI and operational activity for a patient.
        </p>
      </div>

      {/* Search */}

      <div className="rounded-xl border bg-white p-5 shadow-sm">

        <div className="flex gap-3">

          <input
            type="number"
            placeholder="Patient ID"
            value={patientId}
            onChange={(e) =>
              setPatientId(e.target.value)
            }
            className="rounded-lg border px-3 py-2"
          />

          <button
            onClick={loadAudit}
            disabled={loading}
            className="rounded-lg bg-black px-5 py-2 text-white disabled:opacity-50 cursor-pointer"
          >
            {loading ? "Loading..." : "Search"}
          </button>

        </div>

        {error && (
          <p className="mt-3 text-sm text-red-600">
            {error}
          </p>
        )}

      </div>

      {/* Timeline */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Activity Timeline
        </h2>

        {logs.length === 0 ? (
          <p className="mt-4 text-gray-500">
            No audit events found.
          </p>
        ) : (
          <div className="mt-6 space-y-4">

            {logs.map((log) => (

              <div
                key={log.id}
                className="rounded-lg border p-4"
              >

                <div className="flex flex-wrap items-center justify-between gap-3">

                  <div>
                    <p className="font-semibold">
                      {log.action}
                    </p>

                    <p className="text-sm text-gray-500">
                      {new Date(
                        log.created_at
                      ).toLocaleString()}
                    </p>
                  </div>

                  {log.entity_type && (
                    <span className="rounded-full border px-3 py-1 text-xs">
                      {log.entity_type}
                      {log.entity_id
                        ? ` #${log.entity_id}`
                        : ""}
                    </span>
                  )}

                </div>

                <div className="mt-3 grid grid-cols-1 gap-2 text-sm md:grid-cols-2">

                  <p>
                    <span className="font-medium">
                      Patient:
                    </span>{" "}
                    {log.patient_id ?? "-"}
                  </p>

                  <p>
                    <span className="font-medium">
                      Call:
                    </span>{" "}
                    {log.call_id ?? "-"}
                  </p>

                  <p>
                    <span className="font-medium">
                      User:
                    </span>{" "}
                    {log.user_id ?? "System"}
                  </p>

                  <p className="break-all">
                    <span className="font-medium">
                      Correlation:
                    </span>{" "}
                    {log.correlation_id ?? "-"}
                  </p>

                </div>

                {log.details && (
                  <details className="mt-4">

                    <summary className="cursor-pointer text-sm font-medium">
                      View event details
                    </summary>

                    <pre className="mt-3 overflow-x-auto rounded-lg bg-gray-50 p-3 text-xs">
                      {formatDetails(log.details)}
                    </pre>

                  </details>
                )}

              </div>

            ))}

          </div>
        )}

      </div>

    </div>
  )
}
