import apiClient from "./client"
import type { ConsensusAssessment } from "../types/consensus"
import { MOCK_CONSENSUS } from "../mock/mockData"

export async function getCallConsensus(
  callId: number
): Promise<ConsensusAssessment> {
  try {
    const response = await apiClient.get(
      `/ai-tools/consensus/call/${callId}`
    )
    if (response.data) return response.data
  } catch {
    // ignore
  }

  return {
    ...MOCK_CONSENSUS,
    call_id: callId,
  }
}
