<template>
  <aside
    :class="[
      mini ? 'w-16' : 'w-52',
      'text-white flex flex-col justify-between bg-blue-600 min-h-screen text-sm transition-all duration-300'
    ]"
  >
    <div>
      <!-- Logo (usa imagens configuradas na aba Geral) -->
      <div class="flex items-center gap-2 p-[0.7rem] text-xl font-bold bg-[#1d4ed8]" :class="mini ? 'justify-center' : ''">
        <router-link to="/dashboard" class="flex items-center gap-2 cursor-pointer select-none">
          <template v-if="mini">
            <img v-if="logoSidebarMiniUrl" :src="logoSidebarMiniUrl" alt="logo-mini" class="w-8 h-8 object-contain" />
            <img v-else-if="logoSidebarUrl" :src="logoSidebarUrl" alt="logo" class="w-8 h-8 object-contain" />
            <Zap v-else :class="['bg-white text-blue-600 flex items-center p-1 rounded-md w-8 h-8 hover:bg-white hover:text-blue-300']" />
          </template>
          <template v-else>
            <template v-if="logoSidebarUrl">
              <img :src="logoSidebarUrl" alt="logo" class="h-7 object-contain" />
            </template>
            <template v-else>
              <Zap :class="['bg-white text-blue-600 flex items-center p-1 rounded-md w-6 h-6 hover:bg-white hover:text-blue-300']" />
              <span class="ml-1" v-if="companyName">{{ companyName }}</span>
              <span class="ml-1" v-else>FazEnergy</span>
            </template>
          </template>
        </router-link>
      </div>

      <nav class="px-2 space-y-5">
        <!-- Menu Principal -->
        <div class="mt-3">
          <button v-if="!mini" type="button" @click="principalOpen = !principalOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Menu Principal</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!principalOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || principalOpen">
            <li v-if="isSuperUser || isLicensed || isOperador">
              <router-link to="/dashboard" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Dashboard">
                <LayoutDashboard class="w-4 h-4" />
                <span v-if="!mini">Dashboard</span>
              </router-link>
            </li>
            <!-- Acesso rápido a Fechamentos na sessão principal (somente Licenciado) -->
            <li v-if="isLicensed && !isOperador && !isSuperUser">
              <router-link to="/reports/closures" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Fechamentos">
                <DollarSign class="w-4 h-4" />
                <span v-if="!mini">Fechamentos</span>
              </router-link>
            </li>

            <!-- Banco Saque (somente Licenciado) -->
            <li v-if="isLicensed && !isOperador && !isSuperUser">
              <router-link to="/finance/withdraw-accounts" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Banco Saque">
                <Banknote class="w-4 h-4" />
                <span v-if="!mini">Banco Saque</span>
              </router-link>
            </li>
            
            
            <li v-if="isSuperUser">
              <router-link to="/settings" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Configurações">
                <Settings class="w-4 h-4" />
                <span v-if="!mini">Configurações</span>
              </router-link>
            </li>

            <!-- Relatórios (pai com submenu expansível) -->
            <li v-if="isSuperUser || isOperador">
              <button type="button" @click="reportsOpen = !reportsOpen" :class="['w-full flex items-center p-2 rounded hover:bg-blue-800 cursor-pointer', mini ? 'justify-center' : 'justify-between']" title="Relatórios">
                <span class="flex items-center gap-2">
                  <FileText class="w-4 h-4" />
                  <span v-if="!mini">Relatórios</span>
                </span>
                <span v-if="!mini" class="ml-2 inline-flex items-center">
                  <ChevronRight v-if="!reportsOpen" class="w-3.5 h-3.5 opacity-80" />
                  <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
                </span>
              </button>
              <ul v-show="reportsOpen && !mini" class="ml-6 mt-1 space-y-1">
                <!-- Relatório Geral (Superadmin e Operador) -->
                <li v-if="isSuperUser || isOperador">
                  <router-link to="/reports/general" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Relatório Geral">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Relatório Geral</span>
                  </router-link>
                </li>
                <!-- Relatório de Pontos (Superadmin e Operador) -->
                <li v-if="isSuperUser || isOperador">
                  <router-link to="/reports/points" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Relatório de Pontos">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Relatório de Pontos</span>
                  </router-link>
                </li>
                <!-- Relatório de Fechamentos (Superadmin e Operador) -->
                <li v-if="isSuperUser || isOperador">
                  <router-link to="/reports/closures" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Relatório de Fechamentos">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Fechamentos</span>
                  </router-link>
                </li>
                <!-- Relatório de Bônus (Superadmin e Operador) -->
                <li v-if="isSuperUser || isOperador">
                  <router-link to="/reports/bonus" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Relatório de Bônus">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Relatório de Bônus</span>
                  </router-link>
                </li>
                <!-- Contas Virtuais (Superadmin e Operador) -->
                <li v-if="isSuperUser || isOperador">
                  <router-link to="/reports/virtual-accounts" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Contas Virtuais">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Contas Virtuais</span>
                  </router-link>
                </li>
              </ul>
            </li>
          </ul>
        </div>

        <!-- Gerenciar Usuários (superadmin apenas) -->
        <div v-if="isSuperUser">
          <button v-if="!mini" type="button" @click="usersOpen = !usersOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Gerenciar Usuários</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!usersOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || usersOpen">
            <li>
              <router-link to="/admin/users" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Usuários">
                <Users class="w-4 h-4" /><span v-if="!mini">Usuários</span>
              </router-link>
            </li>
            <!--
            <li>
              <router-link to="/admin/permissions" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Perfis">
                <User class="w-4 h-4" /><span v-if="!mini">Perfis</span>
              </router-link>
            </li>
            -->
            <li>
              <router-link to="/admin/groups" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Grupos">
                <Link class="w-4 h-4" /><span v-if="!mini">Grupos</span>
              </router-link>
            </li>
            <li>
              <router-link to="/admin/schedules" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Rotinas (Dev)">
                <Clock class="w-4 h-4" /><span v-if="!mini">Rotinas (Dev)</span>
              </router-link>
            </li>
          </ul>
        </div>

        

          <!-- Rede (Licenciado, Operador ou Superadmin) -->
          <div v-if="isLicensed || isOperador || isSuperUser">
          <button v-if="!mini" type="button" @click="redeOpen = !redeOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Rede</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!redeOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || redeOpen">
            <li v-if="!isSuperUser && !isOperador">
              <router-link to="/network/directs" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Diretos">
                <ArrowRight class="w-4 h-4" />
                <span v-if="!mini">Diretos</span>
              </router-link>
            </li>
            <li>
              <router-link to="/network/downlines" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Rede Completa">
                <Users class="w-4 h-4" />
                <span v-if="!mini">Rede Completa</span>
              </router-link>
            </li>
            <li v-if="isOperador || isSuperUser">
              <router-link to="/network/adesions" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Adesões">
                <Users class="w-4 h-4" />
                <span v-if="!mini">Adesões</span>
              </router-link>
            </li>
            <li v-if="!isOperador">
              <router-link to="/network/tree" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Árvore da Rede">
                <TreePine class="w-4 h-4" />
                <span v-if="!mini">Árvore da Rede</span>
              </router-link>
            </li>
            
          </ul>
        </div>

        <!-- Financeiro (Operador/Superadmin) -->
        <div v-if="isOperador || isSuperUser">
          <button v-if="!mini" type="button" @click="financeOpen = !financeOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Financeiro</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!financeOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || financeOpen">
            <li>
              <router-link to="/finance/withdrawals" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Solicitações de Saque">
                <FileText class="w-4 h-4" />
                <span v-if="!mini">Solicitações de Saque</span>
              </router-link>
            </li>
            <li>
              <router-link to="/finance/virtual-accounts" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Saldo de Contas">
                <Users class="w-4 h-4" />
                <span v-if="!mini">Saldo de Contas</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Licenciados (Operador/Superadmin) -->
        <div v-if="isOperador || isSuperUser">
          <button v-if="!mini" type="button" @click="licOpen = !licOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Licenciados</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!licOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || licOpen">
            <li>
              <router-link to="/licensed" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Cadastro de Licenciados">
                <Users class="w-4 h-4" />
                <span v-if="!mini">Cadastro</span>
              </router-link>
            </li>
            <li>
              <router-link to="/documents/review" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Revisar Documentos">
                <FileCheck class="w-4 h-4" />
                <span v-if="!mini">Revisar Docs</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Usina (Licenciado, Operador ou Superadmin) -->
        <div v-if="isLicensed || isOperador || isSuperUser">
          <button v-if="!mini" type="button" @click="usinaOpen = !usinaOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Usina</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!usinaOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || usinaOpen">
            <li>
              <router-link to="/proposal" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Proposta">
                <FileText class="w-4 h-4" />
                <span v-if="!mini">Proposta</span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Geral (Licenciado, Operador ou Superadmin) -->
      <div v-if="isLicensed || isOperador || isSuperUser">
          <button v-if="!mini" type="button" @click="geralOpen = !geralOpen" class="w-full uppercase text-[10px] text-blue-200 mb-2 tracking-wider flex items-center justify-between">
            <span>Geral</span>
            <span class="inline-flex items-center">
              <ChevronRight v-if="!geralOpen" class="w-3.5 h-3.5 opacity-80" />
              <ChevronDown v-else class="w-3.5 h-3.5 opacity-80" />
            </span>
          </button>
          <ul class="space-y-1" v-show="mini || geralOpen">
            <li><a href="#" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Materiais"><Book class="w-4 h-4" /><span v-if="!mini">Materiais</span></a></li>
            <li><a href="#" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Suporte"><LifeBuoy class="w-4 h-4" /><span v-if="!mini">Suporte</span></a></li>
            <li v-if="!isOperador">
              <router-link to="/career-plan" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Plano de Carreira"><BarChart class="w-4 h-4" /><span v-if="!mini">Plano de Carreira</span></router-link>
            </li>
            <li>
              <router-link to="/profile" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Meu Perfil">
                <UserCircle class="w-4 h-4" />
                <span v-if="!mini">Meu Perfil</span>
              </router-link>
            </li>
            <li>
              <router-link to="/company" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Minhas Empresas">
                <Users class="w-4 h-4" />
                <span v-if="!mini">Minhas Empresas</span>
              </router-link>
            </li>
          </ul>
        </div>
      </nav>
    </div>

    <!-- Rodapé -->
    <div class="p-4 border-t border-blue-700 text-[10px] text-blue-200 bg-[#1d4ed8] leading-tight">
      <div v-if="!mini">
        Versão: 18.1.5<br />
        <hr class="my-2 border-blue-500" />
        Copyright© 2025 - FazEnergy
      </div>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  mini: {
    type: Boolean,
    default: false
  }
})

import {
  Zap, LayoutDashboard, FileText, FileCheck, Settings, Users, User, Link,
  ArrowRight, TreePine, Book, LifeBuoy, BarChart, UserCircle,
  ChevronDown, ChevronRight, DollarSign, Banknote, Clock
} from 'lucide-vue-next'

import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useSettingsStore } from '@/store/settings'

const auth = useAuthStore()
const isSuperUser = computed(() => auth.user?.is_superuser === true)
const groups = computed(() => auth.user?.groups || [])

const isLicensed = computed(() => groups.value.includes('Licenciado'))
const isOperador = computed(() => groups.value.includes('Operador'))

// Estados de expansão das seções
const reportsOpen = ref(false)
const principalOpen = ref(true)
const usersOpen = ref(true)
const redeOpen = ref(true)
const licOpen = ref(true)
const geralOpen = ref(true)
const usinaOpen = ref(true)
const financeOpen = ref(true)
// Carrega logos e nome da empresa do store de configurações
const settingsStore = useSettingsStore()
onMounted(() => settingsStore.loadFromStorage())
const logoSidebarUrl = computed(() => settingsStore.settings.general.logo_sidebar_data_url)
const logoSidebarMiniUrl = computed(() => settingsStore.settings.general.logo_sidebar_mini_data_url)
const companyName = computed(() => settingsStore.settings.general.company_name)
</script>
