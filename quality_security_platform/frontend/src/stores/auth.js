import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
  }),
  actions: {
    async login(credentials) {
      this.loading = true
      try {
        const response = await api.login(credentials)
        this.user = response.data
        this.isAuthenticated = true
        return { success: true }
      } catch (error) {
        return { success: false, error: error.response?.data?.error || '登录失败' }
      } finally {
        this.loading = false
      }
    },
    async logout() {
      try {
        await api.logout()
      } finally {
        this.user = null
        this.isAuthenticated = false
      }
    },
    async fetchCurrentUser() {
      try {
        const response = await api.getCurrentUser()
        this.user = response.data
        this.isAuthenticated = true
      } catch {
        this.user = null
        this.isAuthenticated = false
      }
    },
  },
})