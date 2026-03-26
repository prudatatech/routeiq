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
import { useState, useEffect } from 'react'
import { authAPI } from '@/services/api'
import { Spinner } from '@/components/ui'

function PrivateRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: string[] }) {
  const token = useAuthStore(s => s.token)
  const role = useAuthStore(s => s.role)
  
  if (!token) return <Navigate to="/login" replace />
  
  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/dashboard" replace />
  }
  
  return <>{children}</>
}

function SyncWrapper({ children }: { children: React.ReactNode }) {
  const { token, setAuth, refreshToken } = useAuthStore()
  const [isSyncing, setIsSyncing] = useState(!!token)

  useEffect(() => {
    async function sync() {
      if (token) {
        try {
          const userData = await authAPI.sync()
          setAuth(token, refreshToken || '', userData.role)
        } catch (err: any) {
          console.error('CRITICAL: Sync failed with detail:', {
            status: err.response?.status,
            data: err.response?.data,
            message: err.message
          })
          // If sync specifically fails with 401, we might be hitting a key issue
        }
      }
      setIsSyncing(false)
    }
    sync()
  }, []) // Run once on mount

  if (isSyncing) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center gap-4">
        <Spinner size={40} className="text-yellow-500" />
        <p className="text-[10px] font-black uppercase text-slate-400 tracking-[0.3em]">Synching Intelligence...</p>
      </div>
    )
  }

  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <SyncWrapper>
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
      </SyncWrapper>
    </BrowserRouter>
  )
}
