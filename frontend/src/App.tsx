import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom"

import MainLayout from "./layouts/MainLayout"
import ProtectedRoute from "./routes/ProtectedRoute"
import RoleProtectedRoute from "./components/RoleProtectedRoute"

import Dashboard from "./pages/Dashboard"
import Patients from "./pages/Patients"
import PatientDetails from "./pages/PatientDetails"
import Campaigns from "./pages/Campaigns"
import CampaignDetails from "./pages/CampaignDetails"
import Queue from "./pages/Queue"
import QueueDetails from "./pages/QueueDetails"
import Calls from "./pages/Calls"
import CallDetails from "./pages/CallDetails"
import Escalations from "./pages/Escalations"
import EscalationDetails from "./pages/EscalationDetails"
import DocumentationDetails from "./pages/DocumentationDetails"
import Analytics from "./pages/Analytics"
import Audit from "./pages/Audit"
import SafetyEvaluation from "./pages/SafetyEvaluation"
import Login from "./pages/Login"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/patients/:patientId" element={<PatientDetails />} />

            <Route
              path="/campaigns"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CAMPAIGN_MANAGER",
                  ]}
                >
                  <Campaigns />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/campaigns/:campaignId"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CAMPAIGN_MANAGER",
                  ]}
                >
                  <CampaignDetails />
                </RoleProtectedRoute>
              }
            />

            <Route
              path="/queue"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CAMPAIGN_MANAGER",
                  ]}
                >
                  <Queue />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/queue/:queueItemId"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CAMPAIGN_MANAGER",
                  ]}
                >
                  <QueueDetails />
                </RoleProtectedRoute>
              }
            />

            <Route path="/calls" element={<Calls />} />
            <Route path="/calls/:callId" element={<CallDetails />} />

            <Route
              path="/escalations"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CLINICAL_REVIEWER",
                  ]}
                >
                  <Escalations />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/escalations/:id"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CLINICAL_REVIEWER",
                  ]}
                >
                  <EscalationDetails />
                </RoleProtectedRoute>
              }
            />

            <Route path="/documentation/:id" element={<DocumentationDetails />} />
            <Route path="/analytics" element={<Analytics />} />

            <Route
              path="/audit"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CLINICAL_REVIEWER",
                  ]}
                >
                  <Audit />
                </RoleProtectedRoute>
              }
            />

            <Route
              path="/safety"
              element={
                <RoleProtectedRoute
                  allowedRoles={[
                    "PLATFORM_ADMIN",
                    "HOSPITAL_ADMIN",
                    "CLINICAL_REVIEWER",
                  ]}
                >
                  <SafetyEvaluation />
                </RoleProtectedRoute>
              }
            />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
