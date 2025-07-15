// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Auth/Login.vue'
import PreRegister from '../views/Auth/PreRegister.vue'
import Dashboard from '../views/Dashboard.vue'
import Network from '../views/Network.vue'
import Reports from '../views/Reports.vue'
import Profile from '../views/Profile.vue'
import Settings from '../views/Settings.vue'
import AccessDenied from '../views/AccessDenied.vue'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/preRegister', name: 'PreRegister', component: PreRegister, meta: { requiresAuth: true } },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/network', component: Network, meta: { requiresAuth: true } },
  { path: '/reports', component: Reports, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/settings', component: Settings, meta: { requiresAuth: true, requiresSuperuser: true  } }, 
  { path: '/accessDenied', name: 'accessDenied', component: AccessDenied },
]


const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Guarda de rota
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('accessToken')

   // Já protege rota normal
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // ✅ Protege rota se exige superuser
  if (to.meta.requiresSuperuser) {
    // Pegue do store se já carregou o profile
    const auth = useAuthStore()

    if (!auth.user) {
      // Se não tem user, force buscar o profile
      await auth.fetchProfile()
    }

    if (!auth.user?.is_superuser) {
      return next('/accessDenied')  // ✅ Usa o path que você definiu!
    }

  }

  
  // Já faz a proteção para login
  if (to.path === '/login' && token) {
    return next('/dashboard')
  }

  next()

})

export default router


