import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import {
  getDocumentation,
  writeDocumentationToEhr,
} from "../api/documentation"

import type { OutreachDocumentation } from "../types/documentation"

function parseJsonList(value: string | null | undefined): string[] {
  if (!value) return []

  try {
    const parsed = JSON.parse(value)

    if (Array.isArray(parsed)) {
      return parsed
    }

    return []
  } catch {
    return []
  }
}

export default function DocumentationDetails() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [documentation, setDocumentation] =
    useState<OutreachDocumentation | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [writing, setWriting] = useState(false)
  const [writeResult, setWriteResult] = useState("")

  useEffect(() => {
    if (id) {
      loadDocumentation(Number(id))
    }
  }, [id])

  async function loadDocumentation(documentationId: number) {
    try {
      setLoading(true)
      setError("")

      const data = await getDocumentation(documentationId)

      setDocumentation(data)
    } catch (err) {
      console.error(err)
      setError("Failed to load documentation")
    } finally {
      setLoading(false)
    }
  }

  async function handleWriteToEhr() {
    if (!documentation) return

    try {
      setWriting(true)
      setWriteResult("")
      setError("")

      const result = await writeDocumentationToEhr(
        documentation.id
      )

      console.log(result)

      setWriteResult(
        "Documentation successfully written to the mock EHR."
      )
    } catch (err) {
      console.error(err)
      setError("Failed to write documentation to EHR")
    } finally {
      setWriting(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        Loading documentation...
      </div>
    )
  }

  if (!documentation) {
    return (
      <div className="p-6">

        <p className="text-red-600">
          Documentation not found.
        </p>

        <button
          onClick={() => navigate(-1)}
          className="mt-4 rounded-lg border px-4 py-2"
        >
          Go Back
        </button>

      </div>
    )
  }

  const symptoms = parseJsonList(
    documentation.symptoms
  )

  const medicationConcerns = parseJsonList(
    documentation.medication_concerns
  )

  const patientQuestions = parseJsonList(
    documentation.patient_questions
  )

  const redFlags = parseJsonList(
    documentation.red_flags
  )

  return (
    <div className="space-y-6 p-6">

      {/* Header */}

      <div>

        <button
          onClick={() => navigate(-1)}
          className="mb-3 text-sm text-gray-500 hover:text-gray-900"
        >
          ← Back
        </button>

        <h1 className="text-2xl font-bold">
          Outreach Documentation
        </h1>

        <p className="mt-1 text-gray-500">
          Documentation #{documentation.id}
        </p>

      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {writeResult && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-green-700">
          {writeResult}
        </div>
      )}

      {/* Metadata */}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Patient
          </p>

          <p className="mt-2 text-lg font-semibold">
            #{documentation.patient_id}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Call
          </p>

          <p className="mt-2 text-lg font-semibold">
            #{documentation.call_id}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Risk
          </p>

          <p className="mt-2 text-lg font-semibold">
            {documentation.triage_risk_level}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Action
          </p>

          <p className="mt-2 text-lg font-semibold">
            {documentation.recommended_action}
          </p>
        </div>

      </div>

      {/* Summary */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Outreach Summary
        </h2>

        <p className="mt-4 whitespace-pre-wrap text-gray-700">
          {documentation.summary}
        </p>

      </section>

      {/* Symptoms */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Symptoms
        </h2>

        {symptoms.length === 0 ? (
          <p className="mt-3 text-gray-500">
            No symptoms recorded.
          </p>
        ) : (
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {symptoms.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        )}

      </section>

      {/* Medication Concerns */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Medication Concerns
        </h2>

        {medicationConcerns.length === 0 ? (
          <p className="mt-3 text-gray-500">
            No medication concerns recorded.
          </p>
        ) : (
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {medicationConcerns.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        )}

      </section>

      {/* Patient Questions */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Patient Questions
        </h2>

        {patientQuestions.length === 0 ? (
          <p className="mt-3 text-gray-500">
            No patient questions recorded.
          </p>
        ) : (
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {patientQuestions.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        )}

      </section>

      {/* Red Flags */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Red Flags
        </h2>

        {redFlags.length === 0 ? (
          <p className="mt-3 text-gray-500">
            No red flags recorded.
          </p>
        ) : (
          <ul className="mt-3 list-disc space-y-2 pl-5">
            {redFlags.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        )}

      </section>

      {/* Escalation */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Escalation
        </h2>

        <div className="mt-4 space-y-3">

          <p>
            <span className="font-medium">
              Escalation Created:
            </span>{" "}
            {documentation.escalation_created
              ? "Yes"
              : "No"}
          </p>

          {documentation.escalation_reason && (
            <p>
              <span className="font-medium">
                Reason:
              </span>{" "}
              {documentation.escalation_reason}
            </p>
          )}

        </div>

      </section>

      {/* Follow-up */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Follow-up
        </h2>

        <p className="mt-3">
          <span className="font-medium">
            Required:
          </span>{" "}
          {documentation.follow_up_required
            ? "Yes"
            : "No"}
        </p>

        {documentation.follow_up_notes && (
          <p className="mt-3 whitespace-pre-wrap text-gray-700">
            {documentation.follow_up_notes}
          </p>
        )}

      </section>

      {/* EHR */}

      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Mock EHR
        </h2>

        <p className="mt-2 text-sm text-gray-500">
          This writes the outreach documentation to the
          mock EHR. It does not modify medications,
          diagnoses, or other clinical records.
        </p>

        <button
          onClick={handleWriteToEhr}
          disabled={writing}
          className="mt-4 rounded-lg bg-black px-5 py-2 text-white disabled:opacity-50"
        >
          {writing
            ? "Writing..."
            : "Write to Mock EHR"}
        </button>

      </section>

      {/* Timestamp */}

      <p className="text-sm text-gray-500">
        Created{" "}
        {new Date(
          documentation.created_at
        ).toLocaleString()}
      </p>

    </div>
  )
}
