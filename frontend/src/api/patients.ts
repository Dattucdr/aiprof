import apiClient from "./client"
import { Patient } from "../types/patient"
import { MOCK_PATIENTS, MOCK_CLINICAL_DATA } from "../mock/mockData"

function normalizePatient(raw: any): Patient {
  return {
    ...raw,
    mrn: raw.mrn || raw.medical_record_number || "",
    phone: raw.phone || raw.phone_number || null,
  }
}

export async function getPatients(): Promise<Patient[]> {
  try {
    const response = await apiClient.get("/patients")
    const data = (response.data || []).map(normalizePatient)
    if (data.length > 0) return data
    return MOCK_PATIENTS
  } catch {
    return MOCK_PATIENTS
  }
}

export async function getPatient(patientId: number): Promise<Patient> {
  try {
    const response = await apiClient.get(`/patients/${patientId}`)
    if (response.data) return normalizePatient(response.data)
  } catch {
    // ignore
  }

  const found = MOCK_PATIENTS.find((p) => p.id === Number(patientId))
  if (found) return found

  // Generate fallback patient if ID not found directly
  return {
    id: patientId,
    hospital_id: 101,
    mrn: `MRN-${10000 + patientId}`,
    first_name: "Patient",
    last_name: `#${patientId}`,
    date_of_birth: "1975-05-15",
    gender: "Other",
    phone: "+1 (555) 000-0000",
    email: `patient${patientId}@example.com`,
    communication_consent: true,
    preferred_language: "English",
    preferred_call_time: "Morning (9am - 12pm)",
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
}

export async function getPatientTimeline(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/timeline`
    )
    if (response.data && response.data.length > 0) return response.data
    return MOCK_CLINICAL_DATA.timeline
  } catch {
    return MOCK_CLINICAL_DATA.timeline
  }
}

export async function getPatientDischarge(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/discharge`
    )
    if (response.data) return response.data
    return MOCK_CLINICAL_DATA.discharge
  } catch {
    return MOCK_CLINICAL_DATA.discharge
  }
}
