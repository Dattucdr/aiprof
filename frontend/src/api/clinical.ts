import apiClient from "./client"
import { MOCK_CLINICAL_DATA } from "../mock/mockData"

export async function getPatientEncounters(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/encounters`
    )
    if (response.data && response.data.length > 0) return response.data
    return MOCK_CLINICAL_DATA.encounters
  } catch {
    return MOCK_CLINICAL_DATA.encounters
  }
}

export async function getPatientConditions(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/conditions`
    )
    if (response.data && response.data.length > 0) return response.data
    return MOCK_CLINICAL_DATA.conditions
  } catch {
    return MOCK_CLINICAL_DATA.conditions
  }
}

export async function getPatientMedications(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/medications`
    )
    if (response.data && response.data.length > 0) return response.data
    return MOCK_CLINICAL_DATA.medications
  } catch {
    return MOCK_CLINICAL_DATA.medications
  }
}

export async function getPatientCarePlans(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/care-plans`
    )
    if (response.data && response.data.length > 0) return response.data
    return MOCK_CLINICAL_DATA.carePlans
  } catch {
    return MOCK_CLINICAL_DATA.carePlans
  }
}

export async function getPatientProcedures(patientId: number) {
  try {
    const response = await apiClient.get(
      `/patients/${patientId}/procedures`
    )
    if (response.data && response.data.length > 0) return response.data
    return MOCK_CLINICAL_DATA.procedures
  } catch {
    return MOCK_CLINICAL_DATA.procedures
  }
}
