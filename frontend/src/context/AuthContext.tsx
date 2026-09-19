import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react"
import { getCurrentUser } from "../api/users"
import { CurrentUser } from "../types/auth"

interface AuthContextType {
  token: string | null
  user: CurrentUser | null
  isAuthenticated: boolean
  loading: boolean
  loginUser: (token: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(
  undefined
)

export function AuthProvider({
  children,
}: {
  children: ReactNode
}) {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token")
  )
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)

  async function loadUser() {
    const storedToken = localStorage.getItem("access_token")

    if (!storedToken) {
      setLoading(false)
      return
    }

    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
      setToken(storedToken)
    } catch {
      localStorage.removeItem("access_token")
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUser()
  }, [])

  async function loginUser(newToken: string) {
    localStorage.setItem("access_token", newToken)
    setToken(newToken)

    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
    } catch {
      localStorage.removeItem("access_token")
      setToken(null)
      throw new Error("Unable to load user information")
    }
  }

  function logout() {
    localStorage.removeItem("access_token")
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: !!token && !!user,
        loading,
        loginUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider")
  }

  return context
}
