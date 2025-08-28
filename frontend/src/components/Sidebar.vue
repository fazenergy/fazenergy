<template>
  <aside
    :class="[
      mini ? 'w-16' : 'w-52',
      'text-white flex flex-col justify-between bg-blue-600 min-h-screen text-sm transition-all duration-300'
    ]"
  >
    <div>
      <!-- Logo -->
      <div class="flex items-center gap-2 p-[0.7rem] text-xl font-bold bg-[#1d4ed8]" :class="mini ? 'justify-center' : ''">
        <Zap to="/dashboard" :class="['bg-white text-blue-600 flex items-center p-1 rounded-md w-6 h-6 hover:bg-white hover:text-blue-300', mini ? 'justify-center' : 'gap-2']" />
        <span v-if="!mini">FazEnergy</span>
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
            
            
            <li v-if="isSuperUser">
              <router-link to="/settings" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Configurações">
                <Settings class="w-4 h-4" />
                <span v-if="!mini">Configurações</span>
              </router-link>
            </li>

            <!-- Relatórios (pai com submenu expansível) -->
            <li v-if="isSuperUser">
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
                <li>
                  <router-link to="/reports/points" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Relatório de Pontos">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Relatório de Pontos</span>
                  </router-link>
                </li>
                <li>
                  <router-link to="/reports/bonus" :class="['flex items-center p-2 rounded hover:bg-blue-800 gap-2']" active-class="bg-blue-800" title="Relatório de Bônus">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-300"></span>
                    <span>Relatório de Bônus</span>
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
            <li><a href="#" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Usuários"><Users class="w-4 h-4" /><span v-if="!mini">Usuários</span></a></li>
            <li><a href="#" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Perfis"><User class="w-4 h-4" /><span v-if="!mini">Perfis</span></a></li>
            <li><a href="#" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Grupos"><Link class="w-4 h-4" /><span v-if="!mini">Grupos</span></a></li>
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
            <li>
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
            
            <li>
              <router-link to="/network/tree" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" active-class="bg-blue-800" title="Árvore da Rede">
                <TreePine class="w-4 h-4" />
                <span v-if="!mini">Árvore da Rede</span>
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
                <FileText class="w-4 h-4" />
                <span v-if="!mini">Revisar Docs</span>
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
            <li><a href="#" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Plano de Carreira"><BarChart class="w-4 h-4" /><span v-if="!mini">Plano de Carreira</span></a></li>
            <li>
              <router-link to="/profile" :class="['flex items-center p-2 rounded hover:bg-blue-800', mini ? 'justify-center' : 'gap-2']" title="Meu Perfil">
                <UserCircle class="w-4 h-4" />
                <span v-if="!mini">Meu Perfil</span>
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
  Zap, LayoutDashboard, FileText, Settings, Users, User, Link,
  ArrowRight, TreePine, Book, LifeBuoy, BarChart, UserCircle,
  ChevronDown, ChevronRight
} from 'lucide-vue-next'

import { computed, ref } from 'vue'
import { useAuthStore } from '@/store/auth'

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
</script>
