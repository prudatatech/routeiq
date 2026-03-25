import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 — auto-refresh token
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
          useAuthStore.getState().setAuth(data.access_token, data.refresh_token, data.role)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          useAuthStore.getState().clearAuth()
          window.location.href = '/login'
        }
      }
    }
    const message = error.response?.data?.detail || 'Something went wrong'
    toast.error(message)
    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }).then(r => r.data),
  register: (data: object) =>
    api.post('/auth/register', data).then(r => r.data),
  sync: () => 
    api.post('/auth/sync').then(r => r.data),
  logout: () => api.post('/auth/logout'),
}

export const vehiclesAPI = {
  list: (params?: object) => api.get('/vehicles', { params }).then(r => r.data),
  get: (id: string) => api.get(`/vehicles/${id}`).then(r => r.data),
  create: (data: object) => api.post('/vehicles', data).then(r => r.data),
  update: (id: string, data: object) => api.patch(`/vehicles/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/vehicles/${id}`),
  summary: () => api.get('/vehicles/summary').then(r => r.data),
}

export const routesAPI = {
  list: (params?: object) => api.get('/routes', { params }).then(r => r.data),
  get: (id: string) => api.get(`/routes/${id}`).then(r => r.data),
  updateStatus: (id: string, status: string) =>
    api.patch(`/routes/${id}/status`, { status }).then(r => r.data),
}

export const optimizationAPI = {
  optimize: (data: object) => api.post('/optimize', data).then(r => r.data),
  predictETA: (data: object) => api.post('/optimize/eta', data).then(r => r.data),
}

export const telemetryAPI = {
  ingest: (data: object) => api.post('/telemetry', data).then(r => r.data),
  history: (vehicleId: string, limit = 100) =>
    api.get(`/telemetry/${vehicleId}/history`, { params: { limit } }).then(r => r.data),
  live: (vehicleId: string) => api.get(`/telemetry/${vehicleId}/live`).then(r => r.data),
}

export const dashboardAPI = {
  kpis: () => api.get('/dashboard/kpis').then(r => r.data),
}

export const usersAPI = {
  list: () => api.get('/users').then(r => r.data),
  update: (id: string, data: object) => api.patch(`/users/${id}`, data).then(r => r.data),
  me: () => api.get('/users/me').then(r => r.data),
}
