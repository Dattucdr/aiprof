import type { UserRole } from "../types/auth"

export const PAGE_PERMISSIONS: Record<
  string,
  UserRole[]
> = {
  "/": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
    "CLINICAL_REVIEWER",
  ],

  "/dashboard": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
    "CLINICAL_REVIEWER",
  ],

  "/patients": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
    "CLINICAL_REVIEWER",
  ],

  "/campaigns": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
  ],

  "/queue": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
  ],

  "/calls": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
    "CLINICAL_REVIEWER",
  ],

  "/escalations": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CLINICAL_REVIEWER",
  ],

  "/analytics": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CAMPAIGN_MANAGER",
    "CLINICAL_REVIEWER",
  ],

  "/audit": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CLINICAL_REVIEWER",
  ],

  "/safety": [
    "PLATFORM_ADMIN",
    "HOSPITAL_ADMIN",
    "CLINICAL_REVIEWER",
  ],
}
