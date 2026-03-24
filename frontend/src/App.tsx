import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import AppLayout from '@/components/ui/AppLayout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import FleetPage from '@/pages/FleetPage'
import RoutesPage from '@/pages/RoutesPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import OptimizePage from '@/pages/OptimizePage'
import SuperadminPage from '@/pages/SuperadminPage'
import AIHubPage from '@/pages/AIHubPage'

function PrivateRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: string[] }) {
  const token = useAuthStore(s => s.token)
  const role = useAuthStore(s => s.role)
  
  if (!token) return <Navigate to="/login" replace />
  
  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="fleet" element={
            <PrivateRoute allowedRoles={['superadmin', 'admin', 'manager']}>
              <FleetPage />
            </PrivateRoute>
          } />
          <Route path="routes" element={<RoutesPage />} />
          <Route path="optimize" element={
            <PrivateRoute allowedRoles={['superadmin', 'admin', 'manager']}>
              <OptimizePage />
            </PrivateRoute>
          } />
          <Route path="analytics" element={
            <PrivateRoute allowedRoles={['superadmin', 'admin', 'manager']}>
              <AnalyticsPage />
            </PrivateRoute>
          } />
          <Route path="superadmin" element={
            <PrivateRoute allowedRoles={['superadmin']}>
              <SuperadminPage />
            </PrivateRoute>
          } />
          <Route path="ai-hub" element={
            <PrivateRoute allowedRoles={['superadmin', 'admin']}>
              <AIHubPage />
            </PrivateRoute>
          } />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
