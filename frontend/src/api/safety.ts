import apiClient from "./client"

import type {
  SafetyEvaluation,
} from "../types/safety"
import { MOCK_SAFETY_EVALUATION } from "../mock/mockData"

export async function getSafetyEvaluation(): Promise<SafetyEvaluation> {
  try {
    const response = await apiClient.get(
      "/safety/evaluation"
    )
    if (response.data) return response.data
    return MOCK_SAFETY_EVALUATION
  } catch {
    return MOCK_SAFETY_EVALUATION
  }
}
