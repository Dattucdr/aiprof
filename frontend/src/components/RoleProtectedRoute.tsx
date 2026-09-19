import { Navigate } from "react-router-dom"

import type { ReactNode } from "react"
import type { UserRole } from "../types/auth"

import { useAuth } from "../context/AuthContext"
import { hasRole } from "../utils/rbac"

interface Props {
  allowedRoles: UserRole[]
  children: ReactNode
}

export default function RoleProtectedRoute({
  allowedRoles,
  children,
}: Props) {

  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="p-6 text-slate-500">
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (!hasRole(user.role, allowedRoles)) {
    return (
      <div className="p-6 space-y-2">
        <h1 className="text-xl font-bold text-red-600">
          Access Denied
        </h1>
        <p className="text-sm text-slate-500">
          Your role ({user.role}) does not have access to this page.
        </p>
      </div>
    )
  }

  return <>{children}</>
}
