import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getEscalations } from "../api/escalations"
import type { Escalation } from "../types/escalation"

export default function Escalations() {
  const navigate = useNavigate()

  const [escalations, setEscalations] = useState<Escalation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const [statusFilter, setStatusFilter] = useState("ALL")
  const [priorityFilter, setPriorityFilter] = useState("ALL")
  const [actionFilter, setActionFilter] = useState("ALL")
  const [search, setSearch] = useState("")

  useEffect(() => {
    loadEscalations()
  }, [])

  async function loadEscalations() {
    try {
      setLoading(true)
      setError("")

      const data = await getEscalations()
      setEscalations(data)
    } catch (err) {
      console.error(err)
      setError("Failed to load escalations")
    } finally {
      setLoading(false)
    }
  }

  const filteredEscalations = useMemo(() => {
    return escalations.filter((item) => {
      const matchesStatus =
        statusFilter === "ALL" || item.status === statusFilter

      const matchesPriority =
        priorityFilter === "ALL" || item.priority === priorityFilter

      const matchesAction =
        actionFilter === "ALL" || item.final_action === actionFilter

      const searchText = search.toLowerCase().trim()

      const matchesSearch =
        !searchText ||
        String(item.id).includes(searchText) ||
        String(item.patient_id).includes(searchText) ||
        String(item.call_id ?? "").includes(searchText)

      return (
        matchesStatus &&
        matchesPriority &&
        matchesAction &&
        matchesSearch
      )
    })
  }, [
    escalations,
    statusFilter,
    priorityFilter,
    actionFilter,
    search,
  ])

  const openCount = escalations.filter(
    (item) => item.status === "OPEN"
  ).length

  const reviewCount = escalations.filter(
    (item) => item.status === "IN_REVIEW"
  ).length

  const criticalCount = escalations.filter(
    (item) => item.priority === "CRITICAL"
  ).length

  const resolvedCount = escalations.filter(
    (item) =>
      item.status === "RESOLVED" || item.status === "CLOSED"
  ).length

  if (loading) {
    return (
      <div className="p-6">
        <p>Loading escalations...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">

      <div>
        <h1 className="text-2xl font-bold">
          Escalations
        </h1>

        <p className="mt-1 text-gray-500">
          Review and manage patient escalations.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Summary */}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Open
          </p>

          <p className="mt-2 text-3xl font-bold">
            {openCount}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            In Review
          </p>

          <p className="mt-2 text-3xl font-bold">
            {reviewCount}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Critical
          </p>

          <p className="mt-2 text-3xl font-bold">
            {criticalCount}
          </p>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">
            Resolved
          </p>

          <p className="mt-2 text-3xl font-bold">
            {resolvedCount}
          </p>
        </div>

      </div>

      {/* Filters */}

      <div className="rounded-xl border bg-white p-5 shadow-sm">

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">

          {/* Search */}

          <div>
            <label className="mb-1 block text-sm font-medium">
              Search
            </label>

            <input
              type="text"
              placeholder="Escalation, patient or call ID"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2"
            />
          </div>

          {/* Status */}

          <div>
            <label className="mb-1 block text-sm font-medium">
              Status
            </label>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full rounded-lg border px-3 py-2"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="IN_REVIEW">In Review</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          {/* Priority */}

          <div>
            <label className="mb-1 block text-sm font-medium">
              Priority
            </label>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full rounded-lg border px-3 py-2"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          {/* Action */}

          <div>
            <label className="mb-1 block text-sm font-medium">
              Final Action
            </label>

            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full rounded-lg border px-3 py-2"
            >
              <option value="ALL">All Actions</option>
              <option value="URGENT_CLINICAL_REVIEW">
                Urgent Clinical Review
              </option>
              <option value="CLINICAL_REVIEW">
                Clinical Review
              </option>
            </select>
          </div>

        </div>

        <div className="mt-4 flex items-center justify-between">

          <p className="text-sm text-gray-500">
            Showing {filteredEscalations.length} of{" "}
            {escalations.length} escalations
          </p>

          <button
            onClick={() => {
              setSearch("")
              setStatusFilter("ALL")
              setPriorityFilter("ALL")
              setActionFilter("ALL")
            }}
            className="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50"
          >
            Clear Filters
          </button>

        </div>

      </div>

      {/* Table */}

      <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

        {filteredEscalations.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No escalations match the selected filters.
          </div>
        ) : (
          <div className="overflow-x-auto">

            <table className="w-full text-left">

              <thead className="border-b bg-gray-50 text-sm">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Patient</th>
                  <th className="px-4 py-3">Priority</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Final Action</th>
                  <th className="px-4 py-3">Source</th>
                  <th className="px-4 py-3">Created</th>
                </tr>
              </thead>

              <tbody>

                {filteredEscalations.map((item) => (

                  <tr
                    key={item.id}
                    onClick={() =>
                      navigate(`/escalations/${item.id}`)
                    }
                    className="cursor-pointer border-b last:border-0 hover:bg-gray-50"
                  >

                    <td className="px-4 py-3 font-medium">
                      #{item.id}
                    </td>

                    <td className="px-4 py-3">
                      Patient #{item.patient_id}
                    </td>

                    <td className="px-4 py-3">
                      {item.priority}
                    </td>

                    <td className="px-4 py-3">
                      {item.status}
                    </td>

                    <td className="px-4 py-3">
                      {item.final_action ?? "-"}
                    </td>

                    <td className="px-4 py-3">
                      {item.source}
                    </td>

                    <td className="px-4 py-3">
                      {new Date(item.created_at).toLocaleString()}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  )
}
