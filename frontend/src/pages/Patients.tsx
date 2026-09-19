import { useEffect, useState } from "react"
import { Search, UserRound } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { getPatients } from "../api/patients"
import { Patient } from "../types/patient"

export default function Patients() {
  const navigate = useNavigate()
  const [patients, setPatients] = useState<Patient[]>([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function loadPatients() {
      try {
        const data = await getPatients()
        setPatients(data)
      } catch (err) {
        console.error(err)
        setError("Unable to load patients.")
      } finally {
        setLoading(false)
      }
    }

    loadPatients()
  }, [])

  const filteredPatients = patients.filter((patient) => {
    const searchText = search.toLowerCase()
    return (
      patient.first_name.toLowerCase().includes(searchText) ||
      patient.last_name.toLowerCase().includes(searchText) ||
      patient.mrn.toLowerCase().includes(searchText) ||
      (patient.phone || "").toLowerCase().includes(searchText)
    )
  })

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900">
          Patients
        </h2>
        <p className="mt-1 text-slate-500">
          Manage patients enrolled in healthcare outreach.
        </p>
      </div>

      {/* Search */}
      <div className="mb-6 rounded-xl border bg-white p-4 shadow-sm">
        <div className="relative max-w-md">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="text"
            placeholder="Search by name, MRN or phone..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-full rounded-lg border py-2.5 pl-10 pr-3 outline-none focus:ring-2 focus:ring-slate-300"
          />
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="rounded-xl border bg-white p-8 text-center">
          <p className="text-slate-500">Loading patients...</p>
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-xl bg-red-50 p-4 text-red-600">
          {error}
        </div>
      )}

      {/* Patient Table */}
      {!loading && !error && (
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="border-b bg-slate-50">
                <tr>
                  <th className="px-6 py-4 text-sm font-semibold">Patient</th>
                  <th className="px-6 py-4 text-sm font-semibold">MRN</th>
                  <th className="px-6 py-4 text-sm font-semibold">Phone</th>
                  <th className="px-6 py-4 text-sm font-semibold">Consent</th>
                  <th className="px-6 py-4 text-sm font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredPatients.map((patient) => (
                  <tr
                    key={patient.id}
                    onClick={() => navigate(`/patients/${patient.id}`)}
                    className="cursor-pointer hover:bg-slate-50"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100">
                          <UserRound size={17} />
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">
                            {patient.first_name} {patient.last_name}
                          </p>
                          <p className="text-xs text-slate-500">
                            ID: {patient.id}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">
                      {patient.mrn}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">
                      {patient.phone || "—"}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={
                          patient.communication_consent
                            ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                            : "rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700"
                        }
                      >
                        {patient.communication_consent
                          ? "Granted"
                          : "Not Granted"}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={
                          patient.is_active
                            ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                            : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
                        }
                      >
                        {patient.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredPatients.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-6 py-10 text-center text-slate-500"
                    >
                      No patients found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
