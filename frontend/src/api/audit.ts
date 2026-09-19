import apiClient from "./client"
import type { AuditLog } from "../types/audit"
import { MOCK_AUDIT_LOGS } from "../mock/mockData"

export async function getPatientAudit(
  patientId: number
): Promise<AuditLog[]> {
  try {
    const response = await apiClient.get(
      `/analytics/audit/${patientId}`
    )
    const data = response.data || []
    if (data.length > 0) return data
  } catch {
    // ignore
  }

  return MOCK_AUDIT_LOGS.filter((log) => log.patient_id === Number(patientId) || log.patient_id === null)
}

export async function getHospitalAuditLogs(): Promise<AuditLog[]> {
  try {
    const response = await apiClient.get(
      "/analytics/audit"
    )
    const data = response.data || []
    if (data.length > 0) return data
    return MOCK_AUDIT_LOGS
  } catch {
    return MOCK_AUDIT_LOGS
  }
}
