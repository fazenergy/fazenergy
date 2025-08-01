import axios from 'axios'
import { API_BASE_URL } from '@/config/settings'

const api = axios.create({
  baseURL: API_BASE_URL
})

// ✅ Interceptor de REQUEST: injeta o token sempre!
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// ✅ Interceptor de RESPONSE: tenta refresh automático
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refreshToken')

      try {
        const res = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
          refresh: refreshToken
        })

        const newAccessToken = res.data.access
        localStorage.setItem('accessToken', newAccessToken)

        // Atualiza header global
        api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`

        return api(originalRequest)
      } catch (err) {
        debugger;
        console.error('Refresh token inválido')
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        //window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
