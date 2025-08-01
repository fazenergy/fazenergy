// src/router/index.js

// ROTAS E PERMISSÕES DE ACESSO
// #########################################################################################
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

import Login from '../views/Auth/Login.vue'
import PreRegister from '../views/Auth/PreRegister.vue'
import Dashboard from '../views/Dashboard.vue'
import Network from '../views/Network.vue'
import Reports from '../views/Reports.vue'
import Profile from '../views/Profile.vue'
import Settings from '../views/Settings.vue'
import AccessDenied from '../views/AccessDenied.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
  {
    path: '/',
    redirect: (to) => {
      const query = to.query
      if (query.ind) return { path: '/preRegister', query }
      return '/login'
    }
  },
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/preRegister', name: 'PreRegister', component: PreRegister, meta: { public: true } },
  

  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true, roles: ['superadmin'] } },
  { path: '/network', component: Network, meta: { requiresAuth: true, roles: ['superadmin', 'afiliado', 'operador'] } },
  { path: '/reports', component: Reports, meta: { requiresAuth: true, roles: ['superadmin'] } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true, roles: ['superadmin', 'afiliado', 'operador'] } },
  { path: '/settings', component: Settings, meta: { requiresAuth: true, roles: ['superadmin'] } },
  { path: '/accessDenied', name: 'accessDenied', component: AccessDenied },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound, meta: { public: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ✅ Guarda de navegação
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  const token = localStorage.getItem('accessToken')

  if (token && !auth.user) {
    try {
      await auth.fetchProfile()
    } catch (e) {
      // Só faz logout e redireciona se a rota exigir autenticação
      if (to.meta.requiresAuth) {
        auth.logout()
        return next('/login')
      } else {
        // Se for rota pública, só limpa o token inválido, mas NÃO redireciona
        auth.logout()
        return next()
      }
    }
  }

  // Agora sim, faz as checagens
  if (to.meta.requiresAuth) {
    if (!token || !auth.user) {
      return next('/login')
    }
    // Checagem de roles
    if (to.meta.roles && to.meta.roles.length > 0) {
      const userGroups = auth.user.groups?.map(g => g.toLowerCase()) || []
      const userRole = auth.user.is_superuser ? 'superadmin' : userGroups[0]
      const allowedRoles = to.meta.roles.map(r => r.toLowerCase())
      if (!allowedRoles.includes(userRole)) {
        return next('/accessDenied')
      }
    }
  }

  // Se já está logado e tenta acessar login, redireciona para dashboard
  if (to.path === '/login' && token && auth.user) {
    return next('/dashboard')
  }

  next()
})
// ...existing code...


export default router
