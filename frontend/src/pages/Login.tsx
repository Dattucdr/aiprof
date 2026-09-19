import { FormEvent, useState } from "react"
import { useNavigate } from "react-router-dom"

import { login } from "../api/auth"
import { useAuth } from "../context/AuthContext"


export default function Login() {
  const navigate = useNavigate()
  const { loginUser } = useAuth()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault()
    setError("")
    setLoading(true)

    try {
      const result = await login({
        email,
        password,
      })

      await loginUser(result.access_token)
      navigate("/")
    } catch {
      setError(
        "Invalid email or password."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-slate-900">
            AIProf
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Healthcare Operations Platform
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >
          <div>
            <label className="mb-1 block text-sm font-medium">
              Email
            </label>

            <input
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="Enter your email"
              required
              className="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-slate-400"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              required
              className="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-slate-400"
            />
          </div>

          {error && (
            <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-slate-900 py-2.5 font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  )
}
