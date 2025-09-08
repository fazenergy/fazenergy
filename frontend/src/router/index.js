// ========================================
// ROUTER PRINCIPAL DO FRONTEND
// ========================================
// Configuração de rotas e permissões de acesso
// #########################################################################################

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// ========================================
// IMPORTAÇÕES DAS VIEWS
// ========================================
// Autenticação
import Login from '../views/Auth/Login.vue'
import PreRegister from '../views/Auth/PreRegister.vue'

// Views principais
import Dashboard from '../views/Dashboard.vue'
import Network from '../views/Network.vue'
import Directs from '../views/Directs.vue'
import Downlines from '../views/Downlines.vue'
import NetworkTree from '../views/NetworkTree.vue'
import Adesions from '../views/Adesions.vue'

// Relatórios
import Reports from '../views/Reports.vue'
import PointsReport from '../views/Reports/PointsReport.vue'
import BonusReport from '../views/Reports/BonusReport.vue'
import GeneralReport from '../views/Reports/GeneralReport.vue'
import ClosuresReport from '../views/Reports/ClosuresReport.vue'
import VirtualAccountsReport from '../views/Reports/VirtualAccountsReport.vue'

// Outras views
import PaymentIframe from '../views/PaymentIframe.vue'
import Profile from '../views/Profile.vue'
import Settings from '../views/Settings.vue'
import AccessDenied from '../views/AccessDenied.vue'
import NotFound from '../views/NotFound.vue'
import Documents from '../views/Documents.vue'
import DocumentsReview from '../views/DocumentsReview.vue'
import LicensedList from '../views/Licensed/List.vue'

// Administração
import AdminUsers from '../views/Admin/Users.vue'
import AdminGroups from '../views/Admin/Groups.vue'
import AdminPermissions from '../views/Admin/Permissions.vue'

// Propostas e Carreira
import ProposalList from '../views/Proposal/List.vue'
import CareerPlan from '../views/CareerPlan.vue'
import WithdrawRequests from '../views/Finance/WithdrawRequests.vue'
import AccountBalances from '../views/Finance/AccountBalances.vue'

// ========================================
// CONFIGURAÇÃO DAS ROTAS
// ========================================
const routes = [
  // ========================================
  // ROTAS PÚBLICAS (SEM AUTENTICAÇÃO)
  // ========================================
  {
    path: '/',
    redirect: (to) => {
      // Redirecionar para pré-cadastro se houver indicador na URL
      const query = to.query
      if (query.ind) return { path: '/preRegister', query }
      return '/login'
    }
  },
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/preRegister', name: 'PreRegister', component: PreRegister, meta: { public: true } },
  

  // ========================================
  // ROTAS AUTENTICADAS (REQUEREM LOGIN)
  // ========================================
  
  // Dashboard principal
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true, roles: ['superadmin', 'licenciado', 'operador'] } },
  
  // Rede e Network
  { path: '/network', component: Network, meta: { requiresAuth: true, roles: ['superadmin', 'afiliado', 'operador', 'licenciado'] } },
  { path: '/network/directs', component: Directs, meta: { requiresAuth: true, roles: ['superadmin', 'licenciado'] } },
  { path: '/network/downlines', component: Downlines, meta: { requiresAuth: true, roles: ['superadmin', 'operador', 'licenciado'] } },
  { path: '/network/adesions', component: Adesions, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/network/tree', component: NetworkTree, meta: { requiresAuth: true, roles: ['superadmin', 'licenciado'] } },
  
  // Propostas
  { path: '/proposal', component: ProposalList, meta: { requiresAuth: true, roles: ['superadmin', 'operador', 'licenciado'] } },
  
  // Relatórios
  { path: '/reports', redirect: '/reports/general' },  // Redirecionar para relatório geral
  { path: '/reports/general', component: GeneralReport, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/reports/points', component: PointsReport, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/reports/bonus', component: BonusReport, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/reports/closures', component: ClosuresReport, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/reports/virtual-accounts', component: VirtualAccountsReport, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },

  // Financeiro
  { path: '/finance/withdrawals', component: WithdrawRequests, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/finance/virtual-accounts', component: AccountBalances, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  
  // Perfil e documentos
  { path: '/profile', component: Profile, meta: { requiresAuth: true, roles: ['superadmin', 'afiliado', 'operador', 'licenciado'] } },
  { path: '/payment', component: PaymentIframe, meta: { requiresAuth: true, roles: ['superadmin', 'afiliado', 'operador', 'licenciado'] } },
  { path: '/documents', component: Documents, meta: { requiresAuth: true, roles: ['superadmin', 'operador', 'licenciado'] } },
  { path: '/documents/review', component: DocumentsReview, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  { path: '/licensed', component: LicensedList, meta: { requiresAuth: true, roles: ['superadmin', 'operador'] } },
  
  // Administração (somente superadmin)
  { path: '/admin/users', component: AdminUsers, meta: { requiresAuth: true, roles: ['superadmin'] } },
  { path: '/admin/groups', component: AdminGroups, meta: { requiresAuth: true, roles: ['superadmin'] } },
  { path: '/admin/permissions', component: AdminPermissions, meta: { requiresAuth: true, roles: ['superadmin'] } },
  { path: '/settings', component: Settings, meta: { requiresAuth: true, roles: ['superadmin'] } },
  
  // Plano de carreira
  { path: '/career-plan', component: CareerPlan, meta: { requiresAuth: true, roles: ['licenciado', 'operador', 'superadmin'] } },
  
  // ========================================
  // ROTAS ESPECIAIS
  // ========================================
  { path: '/accessDenied', name: 'accessDenied', component: AccessDenied },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound, meta: { public: true } }
]

// ========================================
// CONFIGURAÇÃO DO ROUTER
// ========================================
const router = createRouter({
  history: createWebHistory(),
  routes,
  // Sempre inicia do topo ao trocar de rota (ou usa posição salva do navegador)
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { left: 0, top: 0 }
  }
})

// ========================================
// GUARDA DE NAVEGAÇÃO (MIDDLEWARE)
// ========================================
// Verifica autenticação e permissões antes de cada navegação
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  const token = localStorage.getItem('accessToken')

  // Carregar perfil do usuário se houver token mas não houver dados do usuário
  if (token && !auth.user) {
    await auth.fetchProfile()
  }

  // ========================================
  // VERIFICAÇÕES DE AUTENTICAÇÃO E PERMISSÕES
  // ========================================
  
  // Verificar se a rota requer autenticação
  if (to.meta.requiresAuth) {
    // Redirecionar para login se não houver token ou usuário
    if (!token || !auth.user) {
      return next('/login')
    }
    
    // Verificar permissões baseadas em roles
    if (to.meta.roles && to.meta.roles.length > 0) {
      const userGroups = auth.user.groups?.map(g => g.toLowerCase()) || []
      const userRole = auth.user.is_superuser ? 'superadmin' : userGroups[0]
      const allowedRoles = to.meta.roles.map(r => r.toLowerCase())
      
      // Redirecionar para acesso negado se não tiver permissão
      if (!allowedRoles.includes(userRole)) {
        return next('/accessDenied')
      }
    }
  }

  // Redirecionar usuário logado que tenta acessar login
  if (to.path === '/login' && token && auth.user) {
    return next('/dashboard')
  }

  // Permitir navegação
  next()
})

export default router
