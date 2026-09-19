import apiClient from "./client"
import { CurrentUser } from "../types/auth"
import { MOCK_CURRENT_USER } from "../mock/mockData"

export async function getCurrentUser(): Promise<CurrentUser> {
  try {
    const response = await apiClient.get(
      "/auth/me"
    )
    const data = response.data
    return {
      ...data,
      name: data.full_name || data.name || data.email,
    }
  } catch {
    return MOCK_CURRENT_USER
  }
}
