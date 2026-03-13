import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Global 401 → redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (email, password) => api.post('/api/v1/auth/login', { email, password }),
}

// ── Teams ─────────────────────────────────────────────────────────────────────
export const teamsAPI = {
  list: ()           => api.get('/api/v1/teams/'),
  create: (data)     => api.post('/api/v1/teams/', data),
  remove: (id)       => api.delete(`/api/v1/teams/${id}`),
}

// ── Managers ──────────────────────────────────────────────────────────────────
export const managersAPI = {
  list: ()           => api.get('/api/v1/managers/'),
  create: (data)     => api.post('/api/v1/managers/', data),
  update: (id, data) => api.put(`/api/v1/managers/${id}`, data),
  remove: (id)       => api.delete(`/api/v1/managers/${id}`),
}

// ── Employees ─────────────────────────────────────────────────────────────────
export const employeesAPI = {
  list: ()           => api.get('/api/v1/employees/'),
  byManager: ()      => api.get('/api/v1/employees/by-manager'),
  create: (data)     => api.post('/api/v1/employees/', data),
  update: (id, data) => api.put(`/api/v1/employees/${id}`, data),
  remove: (id)       => api.delete(`/api/v1/employees/${id}`),
}

export default api
