import { useEffect, useState } from "react"

import {
  getHospitalAnalytics,
} from "../api/analytics"

import type {
  HospitalAnalytics,
} from "../api/analytics"

export default function Analytics() {

  const [analytics, setAnalytics] =
    useState<HospitalAnalytics | null>(null)

  const [loading, setLoading] = useState(true)

  const [error, setError] = useState("")

  useEffect(() => {
    loadAnalytics()
  }, [])

  async function loadAnalytics() {
    try {
      setLoading(true)
      setError("")

      const data = await getHospitalAnalytics()

      setAnalytics(data)

    } catch (err) {
      console.error(err)

      setError(
        "Failed to load analytics."
      )

    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        Loading analytics...
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="p-6 text-red-600">
        {error || "Analytics unavailable."}
      </div>
    )
  }

  const riskTotal =
    (analytics.risk_distribution?.low || 0) +
    (analytics.risk_distribution?.medium || 0) +
    (analytics.risk_distribution?.high || 0) +
    (analytics.risk_distribution?.critical || 0)

  const totalEscalations =
    analytics.total_escalations ?? analytics.escalations?.total ?? 0

  return (
    <div className="space-y-6 p-6">

      {/* Header */}

      <div className="flex items-center justify-between">

        <div>
          <h1 className="text-2xl font-bold">
            Analytics
          </h1>

          <p className="mt-1 text-gray-500">
            Hospital outreach and patient safety metrics.
          </p>
        </div>

        <button
          onClick={loadAnalytics}
          className="rounded-lg border px-4 py-2 hover:bg-gray-50 cursor-pointer"
        >
          Refresh
        </button>

      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Main Metrics */}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">

        <MetricCard
          title="Patients"
          value={analytics.total_patients}
        />

        <MetricCard
          title="Campaigns"
          value={analytics.total_campaigns}
        />

        <MetricCard
          title="Total Calls"
          value={analytics.total_calls}
        />

        <MetricCard
          title="Active Calls"
          value={analytics.active_calls}
        />

      </div>

      {/* Escalations */}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">

        <MetricCard
          title="Total Escalations"
          value={totalEscalations}
        />

        <MetricCard
          title="Recorded Risk Cases"
          value={riskTotal}
        />

      </div>

      {/* Risk Distribution */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="flex items-center justify-between">

          <div>
            <h2 className="text-lg font-semibold">
              Risk Distribution
            </h2>

            <p className="text-sm text-gray-500">
              Triage risk levels recorded by the AI workflow.
            </p>
          </div>

          <span className="text-sm text-gray-500">
            Total: {riskTotal}
          </span>

        </div>

        <div className="mt-6 space-y-5">

          <RiskBar
            label="Low"
            value={analytics.risk_distribution?.low || 0}
            total={riskTotal}
          />

          <RiskBar
            label="Medium"
            value={analytics.risk_distribution?.medium || 0}
            total={riskTotal}
          />

          <RiskBar
            label="High"
            value={analytics.risk_distribution?.high || 0}
            total={riskTotal}
          />

          <RiskBar
            label="Critical"
            value={analytics.risk_distribution?.critical || 0}
            total={riskTotal}
          />

        </div>

      </div>

      {/* Safety interpretation */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Safety Monitoring
        </h2>

        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">

          <InfoCard
            title="High + Critical"
            value={
              (analytics.risk_distribution?.high || 0) +
              (analytics.risk_distribution?.critical || 0)
            }
            description="Cases requiring closer review."
          />

          <InfoCard
            title="Active Calls"
            value={analytics.active_calls}
            description="Calls currently being processed."
          />

          <InfoCard
            title="Escalations"
            value={totalEscalations}
            description="Escalations created by the workflow."
          />

        </div>

      </div>

    </div>
  )
}


function MetricCard({
  title,
  value,
}: {
  title: string
  value: number
}) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <p className="text-sm text-gray-500">
        {title}
      </p>

      <p className="mt-2 text-3xl font-bold">
        {value}
      </p>

    </div>
  )
}


function RiskBar({
  label,
  value,
  total,
}: {
  label: string
  value: number
  total: number
}) {

  const percentage =
    total === 0
      ? 0
      : Math.round((value / total) * 100)

  return (
    <div>

      <div className="mb-2 flex justify-between text-sm">

        <span className="font-medium">
          {label}
        </span>

        <span className="text-gray-500">
          {value} ({percentage}%)
        </span>

      </div>

      <div className="h-3 overflow-hidden rounded-full bg-gray-100">

        <div
          className="h-full rounded-full bg-gray-800 transition-all duration-300"
          style={{
            width: `${percentage}%`,
          }}
        />

      </div>

    </div>
  )
}


function InfoCard({
  title,
  value,
  description,
}: {
  title: string
  value: number
  description: string
}) {
  return (
    <div className="rounded-lg border p-4">

      <p className="text-sm text-gray-500">
        {title}
      </p>

      <p className="mt-2 text-2xl font-bold">
        {value}
      </p>

      <p className="mt-1 text-xs text-gray-500">
        {description}
      </p>

    </div>
  )
}
