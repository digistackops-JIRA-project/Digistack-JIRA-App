import { defineStore } from 'pinia'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('admin_token') || null,
    email: localStorage.getItem('admin_email') || null,
    error: null,
    loading: false,
  }),

  getters: {
    isLoggedIn: (s) => !!s.token,
  },

  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await authAPI.login(email, password)
        this.token = data.access_token
        this.email = email
        localStorage.setItem('admin_token', data.access_token)
        localStorage.setItem('admin_email', email)
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.email = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_email')
    },
  },
})
