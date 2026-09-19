import { useEffect, useState } from "react"
import {
  ArrowLeft,
  CalendarDays,
  Clock,
  RefreshCw,
  Users,
  Settings,
} from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"

import {
  getCampaign,
  getCampaignEligibilityPreview,
  markCampaignReady,
  startCampaign,
  pauseCampaign,
  resumeCampaign,
  cancelCampaign,
} from "../api/campaigns"
import { getCampaignQueueSummary } from "../api/queue"
import { Campaign } from "../types/campaign"
import { QueueSummary } from "../types/queue"

export default function CampaignDetails() {
  const { campaignId } = useParams()
  const navigate = useNavigate()

  const [campaign, setCampaign] = useState<Campaign | null>(null)
  const [eligibility, setEligibility] = useState<any>(null)
  const [queueSummary, setQueueSummary] = useState<QueueSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState("")

  useEffect(() => {
    if (!campaignId) {
      return
    }

    async function loadCampaign() {
      try {
        const id = Number(campaignId)

        const [campaignData, eligibilityData, queueData] = await Promise.all([
          getCampaign(id),
          getCampaignEligibilityPreview(id),
          getCampaignQueueSummary(id),
        ])

        setCampaign(campaignData)
        setEligibility(eligibilityData)
        setQueueSummary(queueData)
      } catch (err) {
        console.error(err)
        setError("Unable to load campaign.")
      } finally {
        setLoading(false)
      }
    }

    loadCampaign()
  }, [campaignId])

  async function handleCampaignAction(action: () => Promise<any>) {
    setActionLoading(true)
    setActionError("")
    try {
      await action()
      const updatedCampaign = await getCampaign(Number(campaignId))
      setCampaign(updatedCampaign)
    } catch (err: any) {
      console.error(err)
      setActionError(
        err?.response?.data?.detail || "Unable to update campaign."
      )
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div>
        <p className="text-slate-500">Loading campaign...</p>
      </div>
    )
  }

  if (error || !campaign) {
    return (
      <div>
        <button
          onClick={() => navigate("/campaigns")}
          className="mb-5 flex items-center gap-2 text-sm text-slate-600"
        >
          <ArrowLeft size={17} /> Back to Campaigns
        </button>

        <div className="rounded-xl bg-red-50 p-4 text-red-600">
          {error || "Campaign not found."}
        </div>
      </div>
    )
  }

  const completionPercentage =
    queueSummary && queueSummary.total > 0
      ? Math.round((queueSummary.completed / queueSummary.total) * 100)
      : 0

  return (
    <div>
      {/* Back */}
      <button
        onClick={() => navigate("/campaigns")}
        className="mb-5 flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft size={17} /> Back to Campaigns
      </button>

      {/* Header */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-slate-100 p-3">
                <Settings size={21} />
              </div>

              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  {campaign.name}
                </h2>

                <p className="text-sm text-slate-500">
                  Campaign ID: {campaign.id}
                </p>
              </div>
            </div>
          </div>

          <StatusBadge status={campaign.status} />
        </div>

        {campaign.description && (
          <p className="mt-5 border-t pt-5 text-sm text-slate-600">
            {campaign.description}
          </p>
        )}
      </div>

      {/* Configuration */}
      <div className="mt-6">
        <h3 className="mb-4 text-lg font-semibold">
          Campaign Configuration
        </h3>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <InfoCard
            icon={<Settings size={18} />}
            label="Priority"
            value={String(campaign.priority)}
          />

          <InfoCard
            icon={<CalendarDays size={18} />}
            label="Follow-up Window"
            value={`${campaign.follow_up_window_days} days`}
          />

          <InfoCard
            icon={<RefreshCw size={18} />}
            label="Max Retries"
            value={
              campaign.max_retry_attempts === null
                ? "Default"
                : String(campaign.max_retry_attempts)
            }
          />

          <InfoCard
            icon={<Clock size={18} />}
            label="Calling Hours"
            value={
              campaign.calling_start && campaign.calling_end
                ? `${campaign.calling_start} - ${campaign.calling_end}`
                : "Hospital default"
            }
          />
        </div>
      </div>

      {/* Eligibility */}
      <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <Users size={20} />

          <div>
            <h3 className="text-lg font-semibold">Eligibility Preview</h3>

            <p className="text-sm text-slate-500">
              Current patients evaluated against campaign rules.
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-5 sm:grid-cols-3">
          <Metric
            label="Total Patients"
            value={getNumber(eligibility, [
              "total_patients_evaluated",
              "total_patients",
              "total",
              "patient_count",
            ])}
          />

          <Metric
            label="Eligible"
            value={getNumber(eligibility, ["eligible_count", "eligible"])}
          />

          <Metric
            label="Not Eligible"
            value={getNumber(eligibility, [
              "ineligible_count",
              "ineligible",
              "not_eligible",
            ])}
          />
        </div>

        <div className="mt-6 rounded-lg bg-slate-50 p-4">
          <p className="text-sm font-medium text-slate-700">
            Eligibility is decided by the backend.
          </p>

          <p className="mt-1 text-xs text-slate-500">
            The frontend only displays the eligibility result and does not
            reproduce the campaign eligibility rules.
          </p>
        </div>
      </div>

      {/* Outreach Progress */}
      <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            Outreach Progress
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Current status of patients in this campaign's outreach queue.
          </p>
        </div>

        {queueSummary ? (
          <>
            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <QueueMetric label="Total" value={queueSummary.total} />
              <QueueMetric label="Pending" value={queueSummary.pending} />
              <QueueMetric label="Scheduled" value={queueSummary.scheduled} />
              <QueueMetric label="Calling" value={queueSummary.calling} />
              <QueueMetric label="Completed" value={queueSummary.completed} />
              <QueueMetric label="Failed" value={queueSummary.failed} />
              <QueueMetric label="Escalated" value={queueSummary.escalated} />
              <QueueMetric
                label="Retry Scheduled"
                value={queueSummary.retry_scheduled}
              />
            </div>

            <div className="mt-6">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-slate-700">
                  Completion
                </span>
                <span className="text-sm font-semibold text-slate-900">
                  {completionPercentage}%
                </span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-slate-900 transition-all"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
            </div>
          </>
        ) : (
          <p className="mt-5 text-sm text-slate-500">
            No queue information available.
          </p>
        )}
      </div>

      {/* Lifecycle */}
      <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Campaign Lifecycle</h3>

        <div className="mt-5 flex flex-wrap items-center gap-2">
          {[
            "DRAFT",
            "READY",
            "SCHEDULED",
            "RUNNING",
            "PAUSED",
            "COMPLETED",
          ].map((status) => (
            <span
              key={status}
              className={
                status === campaign.status
                  ? "rounded-full bg-slate-900 px-3 py-1.5 text-xs font-medium text-white"
                  : "rounded-full bg-slate-100 px-3 py-1.5 text-xs text-slate-500"
              }
            >
              {status}
            </span>
          ))}
        </div>

        {/* Error */}
        {actionError && (
          <div className="mt-5 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {actionError}
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex flex-wrap gap-3">
          {campaign.status === "DRAFT" && (
            <button
              disabled={actionLoading}
              onClick={() =>
                handleCampaignAction(() => markCampaignReady(campaign.id))
              }
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {actionLoading ? "Updating..." : "Mark Ready"}
            </button>
          )}

          {campaign.status === "READY" && (
            <button
              disabled={actionLoading}
              onClick={() =>
                handleCampaignAction(() => startCampaign(campaign.id))
              }
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {actionLoading ? "Starting..." : "Start Campaign"}
            </button>
          )}

          {campaign.status === "SCHEDULED" && (
            <button
              disabled={actionLoading}
              onClick={() =>
                handleCampaignAction(() => startCampaign(campaign.id))
              }
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
            >
              Start Campaign
            </button>
          )}

          {campaign.status === "RUNNING" && (
            <button
              disabled={actionLoading}
              onClick={() =>
                handleCampaignAction(() => pauseCampaign(campaign.id))
              }
              className="rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              {actionLoading ? "Pausing..." : "Pause Campaign"}
            </button>
          )}

          {campaign.status === "PAUSED" && (
            <button
              disabled={actionLoading}
              onClick={() =>
                handleCampaignAction(() => resumeCampaign(campaign.id))
              }
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {actionLoading ? "Resuming..." : "Resume Campaign"}
            </button>
          )}

          {[
            "DRAFT",
            "READY",
            "SCHEDULED",
            "PAUSED",
            "RUNNING",
          ].includes(campaign.status) && (
            <button
              disabled={actionLoading}
              onClick={() => {
                const confirmed = window.confirm(
                  "Are you sure you want to cancel this campaign?"
                )

                if (!confirmed) {
                  return
                }

                handleCampaignAction(() => cancelCampaign(campaign.id))
              }}
              className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
            >
              Cancel Campaign
            </button>
          )}
        </div>

        <p className="mt-5 text-xs text-slate-500">
          Campaign state transitions are validated by the backend.
        </p>
      </div>
    </div>
  )
}

function InfoCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        {icon}
        {label}
      </div>

      <p className="mt-3 text-xl font-bold text-slate-900">{value}</p>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-slate-50 p-5">
      <p className="text-sm text-slate-500">{label}</p>

      <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  )
}

function QueueMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">
      <p className="text-sm text-slate-500">{label}</p>

      <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  )
}

function getNumber(data: any, keys: string[]): number {
  for (const key of keys) {
    if (data && typeof data[key] === "number") {
      return data[key]
    }
  }

  return 0
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700">
      {status}
    </span>
  )
}
