// src/store/auth.js
import { defineStore } from 'pinia'
import api from '@/services/axios' // Usa o seu axios.js configurado!
import { API_BASE_URL } from '@/config/settings'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('accessToken') || '',
    refreshToken: localStorage.getItem('refreshToken') || '',
  }),

  actions: {
    async login(username, password) {
      const response = await api.post('/api/token/', {
        username,
        password,
      })

      this.accessToken = response.data.access
      this.refreshToken = response.data.refresh

      localStorage.setItem('accessToken', this.accessToken)
      localStorage.setItem('refreshToken', this.refreshToken)

      // Sempre set no Axios global
      api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`

      // Carrega perfil se quiser:
      await this.fetchProfile()
    },

    async fetchProfile() {
      if (!this.accessToken) return

      api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`

      const res = await api.get('/api/core/profile/')
      this.user = res.data
    },

    logout() {
      this.user = null
      this.accessToken = ''
      this.refreshToken = ''
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    },
  },
})
