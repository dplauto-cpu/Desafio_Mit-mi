import { Route, Routes, Navigate } from "react-router"
import { Login } from "../pages/auth/Login"
import { RequireAdmin } from "../admin/components/RequireAdmin"
import { Home } from "../admin/pages/Home"
import { LoginPage } from "../pages/LoginPage"
import { AgentePage } from "../pages/AgentePage"

export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path='/home' element={<RequireAdmin> <Home /> </RequireAdmin>} />
      {/* Demo: sin RequireAdmin mientras el login necesita las claves de Firebase.
          Cuando el equipo lo decida, se envuelve igual que /home. */}
      <Route path='/agentes' element={<AgentePage />} />
    </Routes>
  )
}
