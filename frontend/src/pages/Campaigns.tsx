import { useEffect, useState } from "react"
import { Megaphone, Clock, CalendarDays, RefreshCw } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { getCampaigns } from "../api/campaigns"
import { Campaign } from "../types/campaign"

export default function Campaigns() {
  const navigate = useNavigate()
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function loadCampaigns() {
      try {
        const data = await getCampaigns()
        setCampaigns(data)
      } catch (err) {
        console.error(err)
        setError("Unable to load campaigns.")
      } finally {
        setLoading(false)
      }
    }

    loadCampaigns()
  }, [])

  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-bold">Campaigns</h2>
        <p className="mt-4 text-slate-500">Loading campaigns...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <h2 className="text-2xl font-bold">Campaigns</h2>
        <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-600">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Campaigns</h2>
        <p className="mt-1 text-slate-500">
          Manage post-discharge outreach campaigns.
        </p>
      </div>

      {/* Campaign list */}
      {campaigns.length === 0 ? (
        <div className="rounded-xl border bg-white p-10 text-center shadow-sm">
          <Megaphone size={32} className="mx-auto text-slate-400" />
          <p className="mt-3 font-medium">No campaigns found.</p>
          <p className="mt-1 text-sm text-slate-500">
            Create a campaign from the backend or campaign manager.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-2">
          {campaigns.map((campaign) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              onClick={() => navigate(`/campaigns/${campaign.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function CampaignCard({
  campaign,
  onClick,
}: {
  campaign: Campaign
  onClick: () => void
}) {
  return (
    <div
      onClick={onClick}
      className="cursor-pointer rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-slate-100 p-3">
            <Megaphone size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">{campaign.name}</h3>
            <p className="mt-1 text-xs text-slate-500">
              Campaign ID: {campaign.id}
            </p>
          </div>
        </div>

        <StatusBadge status={campaign.status} />
      </div>

      {/* Description */}
      {campaign.description && (
        <p className="mt-4 text-sm text-slate-600">{campaign.description}</p>
      )}

      {/* Details */}
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <Detail
          icon={<CalendarDays size={16} />}
          label="Follow-up Window"
          value={`${campaign.follow_up_window_days} days`}
        />

        <Detail
          icon={<RefreshCw size={16} />}
          label="Max Retries"
          value={
            campaign.max_retry_attempts !== null
              ? String(campaign.max_retry_attempts)
              : "Default"
          }
        />

        <Detail
          icon={<Clock size={16} />}
          label="Calling Hours"
          value={
            campaign.calling_start && campaign.calling_end
              ? `${campaign.calling_start} - ${campaign.calling_end}`
              : "Hospital default"
          }
        />

        <Detail label="Priority" value={String(campaign.priority)} />
      </div>

      {/* Active */}
      <div className="mt-5 border-t pt-4">
        <span
          className={
            campaign.is_active
              ? "rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700"
              : "rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
          }
        >
          {campaign.is_active ? "Active" : "Inactive"}
        </span>
      </div>
    </div>
  )
}

function Detail({
  icon,
  label,
  value,
}: {
  icon?: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div>
      <div className="flex items-center gap-2 text-xs text-slate-500">
        {icon}
        {label}
      </div>

      <p className="mt-1 text-sm font-medium text-slate-900">{value}</p>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    DRAFT: "bg-slate-100 text-slate-700",
    READY: "bg-blue-50 text-blue-700",
    SCHEDULED: "bg-purple-50 text-purple-700",
    RUNNING: "bg-green-50 text-green-700",
    PAUSED: "bg-yellow-50 text-yellow-700",
    COMPLETED: "bg-slate-100 text-slate-700",
    CANCELLED: "bg-red-50 text-red-700",
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-medium ${
        styles[status] || "bg-slate-100 text-slate-700"
      }`}
    >
      {status}
    </span>
  )
}
