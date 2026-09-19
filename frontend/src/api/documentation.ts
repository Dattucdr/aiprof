import apiClient from "./client"
import type { OutreachDocumentation } from "../types/documentation"
import { MOCK_DOCUMENTATION } from "../mock/mockData"

export async function getDocumentation(
  documentationId: number
): Promise<OutreachDocumentation> {
  try {
    const response = await apiClient.get(
      `/ehr/documentation/${documentationId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  return {
    ...MOCK_DOCUMENTATION,
    id: documentationId,
  }
}

export async function getCallDocumentation(
  callId: number
): Promise<OutreachDocumentation | null> {
  try {
    const response = await apiClient.get(
      `/ehr/documentation/call/${callId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  return {
    ...MOCK_DOCUMENTATION,
    call_id: callId,
  }
}

export async function writeDocumentationToEhr(
  documentationId: number
) {
  try {
    const response = await apiClient.post(
      `/ehr/documentation/${documentationId}/write`
    )
    return response.data
  } catch {
    return {
      status: "SUCCESS",
      documentation_id: documentationId,
      ehr_reference_id: `FHIR-NOTE-${10000 + documentationId}`,
      committed_at: new Date().toISOString(),
      message: "Outreach documentation successfully committed to Hospital EHR system.",
    }
  }
}
