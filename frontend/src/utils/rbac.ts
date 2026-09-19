import { UserRole } from "../types/auth"

export function hasRole(
  userRole: UserRole | undefined,
  allowedRoles: UserRole[]
): boolean {
  if (!userRole) {
    return false
  }

  return allowedRoles.includes(userRole)
}
