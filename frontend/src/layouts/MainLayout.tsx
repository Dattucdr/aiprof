import {
  LayoutDashboard,
  Users,
  Megaphone,
  ListTodo,
  Phone,
  AlertTriangle,
  BarChart3,
  ClipboardList,
  ShieldCheck,
} from "lucide-react"

import {
  NavLink,
  Outlet,
} from "react-router-dom"

import { useAuth } from "../context/AuthContext"
import { hasRole } from "../utils/rbac"
import { PAGE_PERMISSIONS } from "../utils/permissions"


const navigation = [
  {
    name: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Patients",
    path: "/patients",
    icon: Users,
  },
  {
    name: "Campaigns",
    path: "/campaigns",
    icon: Megaphone,
  },
  {
    name: "Queue",
    path: "/queue",
    icon: ListTodo,
  },
  {
    name: "Calls",
    path: "/calls",
    icon: Phone,
  },
  {
    name: "Escalations",
    path: "/escalations",
    icon: AlertTriangle,
  },
  {
    name: "Analytics",
    path: "/analytics",
    icon: BarChart3,
  },
  {
    name: "Audit",
    path: "/audit",
    icon: ClipboardList,
  },
  {
    name: "Safety Evaluation",
    path: "/safety",
    icon: ShieldCheck,
  },
]



export default function MainLayout() {
  const { user, logout } = useAuth()

  const visibleNavigation = navigation.filter((item) => {
    if (!user?.role) return true
    const allowedRoles = PAGE_PERMISSIONS[item.path]
    if (!allowedRoles) return true
    return hasRole(user.role, allowedRoles)
  })

  return (
    <div className="flex min-h-screen bg-slate-50">

      <aside className="w-64 border-r bg-white">

        <div className="border-b px-6 py-5">

          <h1 className="text-xl font-bold text-slate-900">
            AIProf
          </h1>

          <p className="text-sm text-slate-500">
            Healthcare Platform
          </p>

        </div>


        <nav className="space-y-1 p-4">

          {visibleNavigation.map((item) => {


            const Icon = item.icon

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium",
                    isActive
                      ? "bg-slate-900 text-white"
                      : "text-slate-600 hover:bg-slate-100",
                  ].join(" ")
                }
              >

                <Icon size={18} />

                {item.name}

              </NavLink>
            )
          })}

        </nav>

      </aside>


      <main className="flex-1">

        <header className="flex h-16 items-center justify-between border-b bg-white px-6">

          <div>
            <p className="text-sm text-slate-500">
              Hospital Operations
            </p>
          </div>

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white">
              {(user?.name || user?.full_name || "U").charAt(0).toUpperCase()}
            </div>

            <div>
              <p className="text-sm font-medium">
                {user?.name || user?.full_name || "User"}
              </p>

              <p className="text-xs text-slate-500">
                {user?.role || "User"}
              </p>
            </div>

            <button
              onClick={logout}
              className="ml-3 rounded-lg border px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
            >
              Logout
            </button>

          </div>

        </header>


        <section className="p-6">

          <Outlet />

        </section>

      </main>

    </div>
  )
}
