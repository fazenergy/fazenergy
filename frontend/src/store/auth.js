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
      if (!this.accessToken) return

      api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`

      const res = await api.get('/api/core/profile/')
      console.log('[DEBUG] Perfil recebido:', res.data); // TO DO: COMENTAR DEPOIS ( bom pra ver como está chegando o perfil do user logado)
      this.user = res.data
    },

    logout() {
      debugger;
      console.log('[AUTH] logout chamado')
      console.trace('[AUTH] logout chamado')
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
