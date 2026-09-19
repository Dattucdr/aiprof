import { useEffect, useState } from "react"
import {
  ArrowLeft,
  UserRound,
  Phone,
  Mail,
  Calendar,
  Pill,
  HeartPulse,
  ClipboardList,
  Activity,
} from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"

import { getPatient, getPatientDischarge } from "../api/patients"
import {
  getPatientConditions,
  getPatientMedications,
  getPatientCarePlans,
  getPatientProcedures,
} from "../api/clinical"
import { Patient } from "../types/patient"

export default function PatientDetails() {
  const { patientId } = useParams()
  const navigate = useNavigate()

  const [patient, setPatient] = useState<Patient | null>(null)
  const [discharge, setDischarge] = useState<any>(null)
  const [conditions, setConditions] = useState<any[]>([])
  const [medications, setMedications] = useState<any[]>([])
  const [carePlans, setCarePlans] = useState<any[]>([])
  const [procedures, setProcedures] = useState<any[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!patientId) {
      return
    }

    async function loadPatient() {
      try {
        const id = Number(patientId)

        const [
          patientData,
          dischargeData,
          conditionsData,
          medicationsData,
          carePlansData,
          proceduresData,
        ] = await Promise.all([
          getPatient(id),
          getPatientDischarge(id),
          getPatientConditions(id),
          getPatientMedications(id),
          getPatientCarePlans(id),
          getPatientProcedures(id),
        ])

        setPatient(patientData)
        setDischarge(dischargeData)
        setConditions(conditionsData)
        setMedications(medicationsData)
        setCarePlans(carePlansData)
        setProcedures(proceduresData)
      } catch (err) {
        console.error(err)
        setError("Unable to load patient information.")
      } finally {
        setLoading(false)
      }
    }

    loadPatient()
  }, [patientId])

  if (loading) {
    return (
      <div className="p-4">
        <p className="text-slate-500">Loading patient...</p>
      </div>
    )
  }

  if (error || !patient) {
    return (
      <div>
        <button
          onClick={() => navigate("/patients")}
          className="mb-5 flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft size={17} /> Back to Patients
        </button>

        <div className="rounded-xl bg-red-50 p-4 text-red-600">
          {error || "Patient not found."}
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* Back */}
      <button
        onClick={() => navigate("/patients")}
        className="mb-5 flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft size={17} /> Back to Patients
      </button>

      {/* Patient Header */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
              <UserRound size={28} />
            </div>

            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                {patient.first_name} {patient.last_name}
              </h2>

              <p className="text-sm text-slate-500">MRN: {patient.mrn}</p>
            </div>
          </div>

          <span
            className={
              patient.is_active
                ? "rounded-full bg-green-50 px-3 py-1.5 text-sm font-medium text-green-700"
                : "rounded-full bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-600"
            }
          >
            {patient.is_active ? "Active" : "Inactive"}
          </span>
        </div>

        {/* Demographics */}
        <div className="mt-6 grid gap-4 border-t pt-6 sm:grid-cols-2 lg:grid-cols-4">
          <InfoItem
            icon={<Calendar size={17} />}
            label="Date of Birth"
            value={patient.date_of_birth ? String(patient.date_of_birth).split("T")[0] : "—"}
          />

          <InfoItem
            icon={<UserRound size={17} />}
            label="Gender"
            value={patient.gender || "—"}
          />

          <InfoItem
            icon={<Phone size={17} />}
            label="Phone"
            value={patient.phone || "—"}
          />

          <InfoItem
            icon={<Mail size={17} />}
            label="Email"
            value={patient.email || "—"}
          />
        </div>
      </div>

      {/* Discharge */}
      <Section title="Latest Discharge" icon={<Activity size={19} />}>
        {discharge ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <InfoItem
              label="Discharge Date"
              value={
                discharge.discharge_date ||
                discharge.discharge_datetime ||
                "—"
              }
            />

            <InfoItem
              label="Encounter"
              value={
                discharge.encounter_id || discharge.id
                  ? String(discharge.encounter_id || discharge.id)
                  : "—"
              }
            />

            <InfoItem
              label="Status"
              value={
                discharge.discharge_status || discharge.status || "Discharged"
              }
            />
          </div>
        ) : (
          <p className="text-sm text-slate-500">
            No discharge information available.
          </p>
        )}
      </Section>

      {/* Conditions */}
      <Section title="Conditions" icon={<HeartPulse size={19} />}>
        <DataList items={conditions} emptyText="No conditions recorded." />
      </Section>

      {/* Medications */}
      <Section title="Medications" icon={<Pill size={19} />}>
        <DataList items={medications} emptyText="No medications recorded." />
      </Section>

      {/* Care Plans */}
      <Section title="Care Plans" icon={<ClipboardList size={19} />}>
        <DataList items={carePlans} emptyText="No care plans recorded." />
      </Section>

      {/* Procedures */}
      <Section title="Procedures" icon={<Activity size={19} />}>
        <DataList items={procedures} emptyText="No procedures recorded." />
      </Section>
    </div>
  )
}

function InfoItem({
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

function Section({
  title,
  icon,
  children,
}: {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="mt-6 rounded-xl border bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center gap-2">
        {icon}
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      </div>

      {children}
    </div>
  )
}

function DataList({
  items,
  emptyText,
}: {
  items: any[]
  emptyText: string
}) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">{emptyText}</p>
  }

  return (
    <div className="space-y-3">
      {items.map((item, index) => {
        const title =
          item.condition_name ||
          item.medication_name ||
          item.procedure_name ||
          item.title ||
          item.name ||
          item.description ||
          item.code ||
          `Record ${index + 1}`

        const description =
          item.instructions ||
          item.description ||
          item.follow_up_instructions ||
          item.notes ||
          null

        return (
          <div
            key={item.id || index}
            className="rounded-lg bg-slate-50 p-4"
          >
            <p className="text-sm font-medium text-slate-900">{title}</p>

            {description && (
              <p className="mt-1 text-xs text-slate-600">{description}</p>
            )}

            {item.status && (
              <p className="mt-1 text-xs text-slate-500">
                Status: {item.status}
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}
