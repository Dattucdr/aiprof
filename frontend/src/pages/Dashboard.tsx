import { useEffect, useState } from "react"
import {
  Users,
  Megaphone,
  Phone,
  AlertTriangle,
} from "lucide-react"

import {
  getHospitalAnalytics,
  HospitalAnalytics,
} from "../api/analytics"


export default function Dashboard() {
  const [analytics, setAnalytics] = useState<HospitalAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const data = await getHospitalAnalytics()
        setAnalytics(data)
      } catch (err) {
        console.error(err)
        setError("Unable to load dashboard data.")
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [])

  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          Dashboard
        </h2>

        <p className="mt-4 text-slate-500">
          Loading dashboard...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          Dashboard
        </h2>

        <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-600">
          {error}
        </div>
      </div>
    )
  }

  if (!analytics) {
    return null
  }

  const totalEscalations =
    analytics.total_escalations ?? analytics.escalations?.total ?? 0

  const cards = [
    {
      title: "Patients",
      value: analytics.total_patients,
      icon: Users,
    },
    {
      title: "Campaigns",
      value: analytics.total_campaigns,
      icon: Megaphone,
    },
    {
      title: "Total Calls",
      value: analytics.total_calls,
      icon: Phone,
    },
    {
      title: "Escalations",
      value: totalEscalations,
      icon: AlertTriangle,
    },
  ]

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          Dashboard
        </h2>

        <p className="mt-1 text-slate-500">
          Healthcare outreach operations overview.
        </p>
      </div>

      {/* Statistics */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => {
          const Icon = card.icon

          return (
            <div
              key={card.title}
              className="rounded-xl border bg-white p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">
                    {card.title}
                  </p>

                  <p className="mt-2 text-3xl font-bold text-slate-900">
                    {card.value}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-100 p-3">
                  <Icon size={22} className="text-slate-700" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Risk Distribution */}
      <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Risk Distribution
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Current triage assessment distribution.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <RiskCard
            title="Low"
            value={analytics.risk_distribution?.low ?? 0}
          />

          <RiskCard
            title="Medium"
            value={analytics.risk_distribution?.medium ?? 0}
          />

          <RiskCard
            title="High"
            value={analytics.risk_distribution?.high ?? 0}
          />

          <RiskCard
            title="Critical"
            value={analytics.risk_distribution?.critical ?? 0}
          />
        </div>
      </div>

      {/* Active Calls */}
      <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">
              Active Outreach
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Calls currently being processed.
            </p>
          </div>

          <Phone size={22} />
        </div>

        <p className="mt-4 text-3xl font-bold">
          {analytics.active_calls}
        </p>
      </div>
    </div>
  )
}

function RiskCard({
  title,
  value,
}: {
  title: string
  value: number
}) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">
      <p className="text-sm text-slate-500">
        {title}
      </p>

      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value}
      </p>
    </div>
  )
}
