export type UserRole =
  | "PLATFORM_ADMIN"
  | "HOSPITAL_ADMIN"
  | "CAMPAIGN_MANAGER"
  | "CLINICAL_REVIEWER"

export interface CurrentUser {
  id: number
  email: string
  full_name?: string
  name?: string
  role: UserRole
  hospital_id: number | null
}
