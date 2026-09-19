import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import apiClient from "../api/client"
import type { Call } from "../api/calls"
import { processCallTriage, processCallConsensus } from "../api/ai"
import { getCallConsensus } from "../api/consensus"
import { getCallEscalation } from "../api/escalations"
import { getCallDocumentation } from "../api/documentation"

import type { TriagePipelineResponse } from "../types/ai"
import type {
  ConsensusAssessment,
  EscalationAssessment,
} from "../types/consensus"
import type { Escalation } from "../types/escalation"
import type { OutreachDocumentation } from "../types/documentation"

function formatDate(value: string | null) {
  if (!value) return "—"
  return new Date(value).toLocaleString()
}

function statusClass(status: string) {
  switch (status) {
    case "COMPLETED":
      return "bg-green-100 text-green-700 border border-green-200"
    case "IN_PROGRESS":
      return "bg-blue-100 text-blue-700 border border-blue-200"
    case "FAILED":
      return "bg-red-100 text-red-700 border border-red-200"
    default:
      return "bg-slate-100 text-slate-700 border border-slate-200"
  }
}

function riskBadgeClass(risk: string) {
  switch (risk?.toUpperCase()) {
    case "CRITICAL":
      return "bg-red-600 text-white font-bold"
    case "HIGH":
      return "bg-orange-500 text-white font-bold"
    case "MEDIUM":
      return "bg-amber-500 text-white font-medium"
    case "LOW":
      return "bg-emerald-600 text-white font-medium"
    default:
      return "bg-slate-500 text-white font-medium"
  }
}

function parseJson<T>(value: string | T | undefined, fallback: T): T {
  if (!value) return fallback
  if (typeof value === "object") return value as T
  try {
    return JSON.parse(value) as T
  } catch {
    return fallback
  }
}

export default function CallDetails() {
  const { callId } = useParams()
  const navigate = useNavigate()

  const [call, setCall] = useState<Call | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  // AI Pipeline states
  const [triageData, setTriageData] = useState<TriagePipelineResponse | null>(null)
  const [triageLoading, setTriageLoading] = useState(false)
  const [triageError, setTriageError] = useState("")

  const [consensus, setConsensus] = useState<ConsensusAssessment | null>(null)
  const [consensusLoading, setConsensusLoading] = useState(false)
  const [consensusError, setConsensusError] = useState("")

  const [escalation, setEscalation] = useState<Escalation | null>(null)
  const [documentation, setDocumentation] = useState<OutreachDocumentation | null>(null)

  useEffect(() => {
    async function loadCall() {
      if (!callId) return

      try {
        setLoading(true)
        const response = await apiClient.get(`/calls/${callId}`)
        setCall(response.data)
      } catch (err: any) {
        console.error(err)
        setError("Failed to load call details")
      } finally {
        setLoading(false)
      }
    }

    loadCall()
  }, [callId])

  // Load existing consensus
  useEffect(() => {
    async function loadConsensus() {
      if (!callId) return
      try {
        const data = await getCallConsensus(Number(callId))
        setConsensus(data)
      } catch {
        setConsensus(null)
      }
    }

    loadConsensus()
  }, [callId])

  // Load escalation + documentation
  useEffect(() => {
    async function loadProcessingResults() {
      if (!callId) return

      try {
        const [escalationData, documentationData] = await Promise.all([
          getCallEscalation(Number(callId)),
          getCallDocumentation(Number(callId)),
        ])

        setEscalation(escalationData)
        setDocumentation(documentationData)
      } catch (err) {
        console.error("Failed to load processing results:", err)
      }
    }

    loadProcessingResults()
  }, [callId])

  const handleRunTriage = async () => {
    if (!callId) return
    try {
      setTriageLoading(true)
      setTriageError("")
      const result = await processCallTriage(Number(callId))
      setTriageData(result)
    } catch (err: any) {
      console.error(err)
      setTriageError(err?.response?.data?.detail || "Failed to execute AI triage pipeline")
    } finally {
      setTriageLoading(false)
    }
  }

  const handleRunConsensus = async () => {
    if (!callId) return
    try {
      setConsensusLoading(true)
      setConsensusError("")
      const result = await processCallConsensus(Number(callId))
      setConsensus(result.consensus as any)

      // Reload escalation and documentation as consensus may trigger them
      const [escData, docData] = await Promise.all([
        getCallEscalation(Number(callId)),
        getCallDocumentation(Number(callId)),
      ])
      setEscalation(escData)
      setDocumentation(docData)
    } catch (err: any) {
      console.error(err)
      setConsensusError(err?.response?.data?.detail || "Failed to run multi-agent consensus")
    } finally {
      setConsensusLoading(false)
    }
  }

  // Parsed Assessments & Evidence
  const assessmentA = consensus
    ? parseJson<EscalationAssessment>(consensus.assessment_a, {
        assessor: "ASSESSMENT_A",
        risk_level: "UNKNOWN",
        recommended_action: "UNKNOWN",
        evidence: [],
        red_flags: [],
        confidence: 0,
      })
    : null

  const assessmentB = consensus
    ? parseJson<EscalationAssessment>(consensus.assessment_b, {
        assessor: "ASSESSMENT_B",
        risk_level: "UNKNOWN",
        recommended_action: "UNKNOWN",
        evidence: [],
        red_flags: [],
        confidence: 0,
      })
    : null

  const consensusEvidence = consensus
    ? parseJson<string[]>(consensus.evidence, [])
    : []

  const consensusRedFlags = consensus
    ? parseJson<string[]>(consensus.red_flags, [])
    : []

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center space-x-3 text-slate-500">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
          <span>Loading call details...</span>
        </div>
      </div>
    )
  }

  if (error || !call) {
    return (
      <div className="p-8 space-y-4">
        <button
          onClick={() => navigate(-1)}
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Back
        </button>
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          {error || "Call not found"}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="mb-3 text-sm font-medium text-blue-600 hover:underline flex items-center gap-1"
          >
            ← Back to Calls
          </button>

          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Call #{call.id}
            </h1>
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClass(call.status)}`}>
              {call.status}
            </span>
          </div>

          <p className="mt-1 text-sm text-slate-500">
            Outreach Attempt #{call.attempt_number} • Patient #{call.patient_id} • Campaign #{call.campaign_id}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRunTriage}
            disabled={triageLoading || !call.transcript}
            className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {triageLoading ? "Processing Triage..." : "Run AI Triage"}
          </button>

          <button
            onClick={handleRunConsensus}
            disabled={consensusLoading}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {consensusLoading ? "Evaluating Consensus..." : "Evaluate Consensus"}
          </button>
        </div>
      </div>

      {/* Call Information Overview */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-bold text-slate-900 mb-4">
          Call Metadata & Status
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-6">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Outcome</p>
            <p className="mt-1 font-semibold text-slate-900">{call.outcome || "—"}</p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Duration</p>
            <p className="mt-1 font-semibold text-slate-900">
              {call.duration_seconds !== null ? `${call.duration_seconds} sec` : "—"}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Queue Item</p>
            <p className="mt-1 font-semibold text-blue-600 cursor-pointer hover:underline" onClick={() => navigate(`/queue/${call.queue_item_id}`)}>
              #{call.queue_item_id}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Worker ID</p>
            <p className="mt-1 font-mono text-xs text-slate-700">{call.worker_id || "Unassigned"}</p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Started At</p>
            <p className="mt-1 text-xs text-slate-700">{formatDate(call.started_at)}</p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Ended At</p>
            <p className="mt-1 text-xs text-slate-700">{formatDate(call.ended_at)}</p>
          </div>
        </div>
      </div>

      {/* Conversation Transcript Section */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50/50 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Conversation Transcript</h2>
            <p className="text-xs text-slate-500">Audio transcript captured during automated call outreach</p>
          </div>
          {call.transcript && (
            <span className="text-xs bg-slate-200 text-slate-700 px-2.5 py-1 rounded-md font-mono">
              {call.transcript.length} characters
            </span>
          )}
        </div>

        <div className="p-6">
          {call.transcript ? (
            <div className="rounded-xl bg-slate-900 p-5 text-slate-100 font-mono text-sm leading-relaxed whitespace-pre-wrap max-h-72 overflow-y-auto">
              {call.transcript}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500 bg-slate-50">
              No transcript available for this call attempt.
            </div>
          )}
        </div>
      </div>

      {/* Errors */}
      {triageError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-700 space-y-1">
          <p className="font-semibold text-sm">Triage Processing Failed</p>
          <p className="text-xs">{triageError}</p>
        </div>
      )}

      {consensusError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-red-700 space-y-1">
          <p className="font-semibold text-sm">Consensus Evaluation Failed</p>
          <p className="text-xs">{consensusError}</p>
        </div>
      )}

      {/* AI Triage & Intake Results */}
      {triageData && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <span>🤖</span> Voice Intake & Clinical Triage Results
            </h2>
            {triageData.existing && (
              <span className="bg-slate-100 text-slate-600 text-xs px-2.5 py-1 rounded-full font-medium">
                Retrieved from database
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {triageData.intake && (
              <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
                <h3 className="text-md font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center justify-between">
                  <span>Structured Voice Intake</span>
                  <div className="flex gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${triageData.intake.consent_confirmed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                      Consent: {triageData.intake.consent_confirmed ? "Confirmed" : "Missing"}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded ${triageData.intake.identity_verified ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                      ID: {triageData.intake.identity_verified ? "Verified" : "Unverified"}
                    </span>
                  </div>
                </h3>

                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Reported Symptoms</p>
                  {triageData.intake.symptoms && triageData.intake.symptoms.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {triageData.intake.symptoms.map((s, idx) => (
                        <span key={idx} className="bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-md border border-blue-100 font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No symptoms reported</p>
                  )}
                </div>

                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Medication Concerns</p>
                  {triageData.intake.medication_concerns && triageData.intake.medication_concerns.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {triageData.intake.medication_concerns.map((m, idx) => (
                        <span key={idx} className="bg-purple-50 text-purple-700 text-xs px-2.5 py-1 rounded-md border border-purple-100 font-medium">
                          {m}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No medication concerns reported</p>
                  )}
                </div>
              </div>
            )}

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
              <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
                <h3 className="text-md font-bold text-slate-900">Clinical Triage Recommendation</h3>
                <span className={`px-3 py-1 text-xs rounded-full ${riskBadgeClass(triageData.triage.risk_level)}`}>
                  Risk: {triageData.triage.risk_level}
                </span>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Recommended Action</p>
                <div className="bg-slate-900 text-white text-sm font-semibold p-3.5 rounded-lg border border-slate-800">
                  {triageData.triage.recommended_action}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Clinical Evidence</p>
                {triageData.triage.evidence && triageData.triage.evidence.length > 0 ? (
                  <ul className="list-disc list-inside text-xs text-slate-700 space-y-1 bg-slate-50 p-3 rounded-lg border border-slate-100">
                    {triageData.triage.evidence.map((ev, idx) => (
                      <li key={idx}>{ev}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400 italic">No evidence listed</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* F7.3 Assessment A + Assessment B + Consensus Section */}
      {consensus && (
        <div className="space-y-6 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <span>🛡️</span> Multi-Agent Independent Assessments & Consensus
            </h2>
            <span className="bg-indigo-100 text-indigo-700 text-xs px-3 py-1 rounded-full font-semibold">
              Consensus Assessment #{consensus.id}
            </span>
          </div>

          {/* Dual Independent Assessments Grid */}
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            <div className="border-b border-slate-200 px-6 py-4 bg-slate-50">
              <h3 className="text-base font-bold text-slate-900">Independent Escalation Assessments</h3>
              <p className="text-xs text-slate-500">
                Two independent safety assessments retained for auditability and disagreement detection
              </p>
            </div>

            <div className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-2">
              {/* Assessment A */}
              {assessmentA && (
                <div className="rounded-xl border border-slate-200 p-5 space-y-4 bg-white shadow-xs">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h4 className="font-bold text-slate-900">Assessment A</h4>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                      {assessmentA.assessor || "AGENT_A"}
                    </span>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Risk Level</p>
                      <span className={`mt-1 inline-block px-3 py-1 text-xs rounded-full ${riskBadgeClass(assessmentA.risk_level)}`}>
                        {assessmentA.risk_level}
                      </span>
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Recommended Action</p>
                      <p className="mt-1 font-semibold text-sm text-slate-900">{assessmentA.recommended_action}</p>
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Confidence</p>
                      <p className="mt-1 text-sm font-semibold text-slate-800">
                        {((assessmentA.confidence || 0) * 100).toFixed(1)}%
                      </p>
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">Evidence</p>
                      {assessmentA.evidence && assessmentA.evidence.length > 0 ? (
                        <ul className="space-y-1.5">
                          {assessmentA.evidence.map((item, index) => (
                            <li key={index} className="rounded-lg bg-slate-50 p-2.5 text-xs text-slate-700 border border-slate-100">
                              {item}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-slate-400 italic">None</p>
                      )}
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">Red Flags</p>
                      {assessmentA.red_flags && assessmentA.red_flags.length > 0 ? (
                        <ul className="space-y-1.5">
                          {assessmentA.red_flags.map((item, index) => (
                            <li key={index} className="rounded-lg bg-red-50 p-2.5 text-xs text-red-700 border border-red-200 font-medium">
                              {item}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-emerald-600 font-semibold">None</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Assessment B */}
              {assessmentB && (
                <div className="rounded-xl border border-slate-200 p-5 space-y-4 bg-white shadow-xs">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h4 className="font-bold text-slate-900">Assessment B</h4>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                      {assessmentB.assessor || "AGENT_B"}
                    </span>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Risk Level</p>
                      <span className={`mt-1 inline-block px-3 py-1 text-xs rounded-full ${riskBadgeClass(assessmentB.risk_level)}`}>
                        {assessmentB.risk_level}
                      </span>
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Recommended Action</p>
                      <p className="mt-1 font-semibold text-sm text-slate-900">{assessmentB.recommended_action}</p>
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Confidence</p>
                      <p className="mt-1 text-sm font-semibold text-slate-800">
                        {((assessmentB.confidence || 0) * 100).toFixed(1)}%
                      </p>
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">Evidence</p>
                      {assessmentB.evidence && assessmentB.evidence.length > 0 ? (
                        <ul className="space-y-1.5">
                          {assessmentB.evidence.map((item, index) => (
                            <li key={index} className="rounded-lg bg-slate-50 p-2.5 text-xs text-slate-700 border border-slate-100">
                              {item}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-slate-400 italic">None</p>
                      )}
                    </div>

                    <div>
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">Red Flags</p>
                      {assessmentB.red_flags && assessmentB.red_flags.length > 0 ? (
                        <ul className="space-y-1.5">
                          {assessmentB.red_flags.map((item, index) => (
                            <li key={index} className="rounded-lg bg-red-50 p-2.5 text-xs text-red-700 border border-red-200 font-medium">
                              {item}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-xs text-emerald-600 font-semibold">None</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Consensus Result Card */}
          <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            <div className="border-b border-slate-200 px-6 py-4 bg-slate-50">
              <h3 className="text-base font-bold text-slate-900">Deterministic Safety Consensus</h3>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 gap-5 md:grid-cols-4">
                <div className="rounded-lg bg-slate-50 p-4 border border-slate-200/60">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Consensus Status</p>
                  <p className="mt-2 font-bold text-slate-900">
                    {consensus.consensus_reached ? "Reached" : "Not Reached"}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-50 p-4 border border-slate-200/60">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Disagreement</p>
                  <p className="mt-2 font-bold text-slate-900">
                    {consensus.disagreement ? "Detected" : "None"}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-50 p-4 border border-slate-200/60">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Final Risk Level</p>
                  <span className={`mt-2 inline-block px-3 py-1 text-xs rounded-full ${riskBadgeClass(consensus.final_risk_level)}`}>
                    {consensus.final_risk_level}
                  </span>
                </div>

                <div className="rounded-lg bg-slate-50 p-4 border border-slate-200/60">
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Final Action</p>
                  <p className="mt-2 font-bold text-slate-900">{consensus.final_action}</p>
                </div>
              </div>

              {consensus.disagreement && consensus.disagreement_reason && (
                <div className="rounded-lg border border-orange-200 bg-orange-50 p-4 space-y-1">
                  <p className="text-xs font-bold text-orange-800">Disagreement Reason</p>
                  <p className="text-xs text-orange-700">{consensus.disagreement_reason}</p>
                </div>
              )}

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div>
                  <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Consensus Evidence</p>
                  {consensusEvidence.length > 0 ? (
                    <ul className="space-y-2">
                      {consensusEvidence.map((item, index) => (
                        <li key={index} className="rounded-lg bg-slate-50 p-3 text-xs text-slate-700 border border-slate-200/60">
                          {item}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No evidence recorded.</p>
                  )}
                </div>

                <div>
                  <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Consensus Red Flags</p>
                  {consensusRedFlags.length > 0 ? (
                    <ul className="space-y-2">
                      {consensusRedFlags.map((item, index) => (
                        <li key={index} className="rounded-lg bg-red-50 p-3 text-xs text-red-700 border border-red-200 font-medium">
                          {item}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-emerald-600 font-semibold">No red flags recorded.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* F7.4 Escalation Section */}
      {escalation && (
        <div className="rounded-xl border border-red-200 bg-white shadow-sm">
          <div className="border-b border-red-100 px-6 py-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Clinical Escalation
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Escalation generated from the backend consensus workflow.
                </p>
              </div>

              <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
                {escalation.priority}
              </span>
            </div>
          </div>

          <div className="p-6 space-y-5">
            <div className="grid grid-cols-1 gap-5 md:grid-cols-4">
              <div>
                <p className="text-xs text-slate-400">Status</p>
                <p className="mt-1 font-semibold">{escalation.status}</p>
              </div>

              <div>
                <p className="text-xs text-slate-400">Priority</p>
                <p className="mt-1 font-semibold">{escalation.priority}</p>
              </div>

              <div>
                <p className="text-xs text-slate-400">Final Action</p>
                <p className="mt-1 font-semibold">{escalation.final_action || "—"}</p>
              </div>

              <div>
                <p className="text-xs text-slate-400">Source</p>
                <p className="mt-1 font-semibold">{escalation.source}</p>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-slate-700">Reason</p>
              <p className="mt-2 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
                {escalation.reason}
              </p>
            </div>

            {escalation.evidence && (
              <div>
                <p className="text-sm font-medium text-slate-700">Evidence</p>
                <pre className="mt-2 whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
                  {escalation.evidence}
                </pre>
              </div>
            )}

            {escalation.resolution_notes && (
              <div>
                <p className="text-sm font-medium text-slate-700">Resolution Notes</p>
                <p className="mt-2 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
                  {escalation.resolution_notes}
                </p>
              </div>
            )}

            {escalation.resolved_at && (
              <div className="text-sm text-slate-500">
                Resolved: {new Date(escalation.resolved_at).toLocaleString()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* F7.4 Outreach Documentation Section */}
      {documentation && (
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Outreach Documentation
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Structured post-outreach documentation.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                  Generated
                </span>

                <button
                  onClick={() =>
                    navigate(
                      `/documentation/${documentation.id}`
                    )
                  }
                  className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  View Full Documentation
                </button>
              </div>
            </div>

          </div>

          <div className="p-6 space-y-6">
            {/* Summary */}
            <div>
              <p className="text-sm font-medium text-slate-700">Summary</p>
              <p className="mt-2 rounded-lg bg-slate-50 p-4 text-sm leading-6 text-slate-700">
                {documentation.summary}
              </p>
            </div>

            {/* Clinical Information */}
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-medium text-slate-500">Symptoms</p>
                <pre className="mt-2 whitespace-pre-wrap text-sm text-slate-700">
                  {documentation.symptoms || "None"}
                </pre>
              </div>

              <div className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-medium text-slate-500">Medication Concerns</p>
                <pre className="mt-2 whitespace-pre-wrap text-sm text-slate-700">
                  {documentation.medication_concerns || "None"}
                </pre>
              </div>

              <div className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-medium text-slate-500">Patient Questions</p>
                <pre className="mt-2 whitespace-pre-wrap text-sm text-slate-700">
                  {documentation.patient_questions || "None"}
                </pre>
              </div>

              <div className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-medium text-slate-500">Red Flags</p>
                <pre className="mt-2 whitespace-pre-wrap text-sm text-slate-700">
                  {documentation.red_flags || "None"}
                </pre>
              </div>
            </div>

            {/* Decision Information */}
            <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
              <div>
                <p className="text-xs text-slate-400">Triage Risk</p>
                <p className="mt-1 font-semibold">{documentation.triage_risk_level}</p>
              </div>

              <div>
                <p className="text-xs text-slate-400">Recommended Action</p>
                <p className="mt-1 font-semibold">{documentation.recommended_action}</p>
              </div>

              <div>
                <p className="text-xs text-slate-400">Follow-up Required</p>
                <p className="mt-1 font-semibold">{documentation.follow_up_required ? "Yes" : "No"}</p>
              </div>
            </div>

            {documentation.escalation_reason && (
              <div>
                <p className="text-sm font-medium text-slate-700">Escalation Reason</p>
                <p className="mt-2 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
                  {documentation.escalation_reason}
                </p>
              </div>
            )}

            {documentation.follow_up_notes && (
              <div>
                <p className="text-sm font-medium text-slate-700">Follow-up Notes</p>
                <p className="mt-2 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
                  {documentation.follow_up_notes}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
