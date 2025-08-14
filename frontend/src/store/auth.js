// src/store/auth.js

// ✅ Está armazenando o user via fetchProfile() após o login
// ✅ Está usando Pinia com persistência via localStorage
// ✅ Está configurando o header de Authorization no axios

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
      if (!this.accessToken) return null

      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
        const res = await api.get('/api/core/profile/')
        this.user = res.data
        return res.data
      } catch (err) {
        // Token inválido/expirado: limpa estado e não propaga erro em rotas públicas
        this.logout({ silent: true })
        return null
      }
    },

    logout(options = {}) {
      const { silent = false } = options
      if (!silent) {
        console.log('[AUTH] logout chamado')
      }
      this.user = null
      this.accessToken = ''
      this.refreshToken = ''
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    userGroups: (state) => state.user?.groups || [],
    isSuperadmin: (state) => state.user?.is_superuser || state.user?.groups?.includes('Superadmin'),
    isAfiliado: (state) => state.user?.groups?.includes('Afiliado'),
    isOperador: (state) => state.user?.groups?.includes('Operador'),
    isCliente: (state) => state.user?.groups?.includes('Cliente'),
  },
})

//console.log(res.data)
/* explicação do getters:
Isso assume que o backend retorna algo como:
  {
    "id": 1,
    "username": "aquiles",
    "role": "superadmin"
  }

*/
