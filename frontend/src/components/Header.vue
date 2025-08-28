<!-- src/components/Header.vue -->
<template>
  <header class="flex justify-between items-center px-4 py-2 border-b border-gray-200 text-[80%]">
      <!-- Toggle + breadcrumb -->
    <div class="flex items-center gap-3">
      <button @click="$emit('toggle-sidebar')" class="hover:text-blue-600">
        <Menu class="w-5 h-5" />
      </button>
      <nav class="text-sm text-gray-700">
        <ol class="flex items-center gap-2">
          <li v-for="(c, i) in breadcrumbs" :key="i" class="flex items-center gap-2">
            <router-link v-if="c.to" :to="c.to" class="hover:underline">{{ c.label }}</router-link>
            <span v-else class="font-semibold text-gray-900">{{ c.label }}</span>
            <span v-if="i < breadcrumbs.length - 1">/</span>
          </li>
        </ol>
      </nav>
    </div>

    <!-- Lado direito: controles -->
    <div class="flex items-center gap-4">
      <!-- Badge Admin -->
      <span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded">
          {{ displyProfile }}
      </span>

      <!-- Botão tema -->
      <button @click="$emit('toggle-theme')"
        class="relative flex items-center justify-center w-8 h-8 hover:text-blue-600">
        <Sun class="absolute w-[1.2rem] h-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon class="absolute w-[1.2rem] h-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        <span class="sr-only">Alternar tema</span>
      </button>

      <!-- Notificações -->
      <Bell class="w-4 h-4" />

      <!-- Nome user -->
      <span>Olá, {{ displayName }}</span>

      <!-- Logout -->
      <button @click="logout" class="flex items-center gap-1 text-sm hover:underline">
        <LogOut class="w-4 h-4" /> Sair
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Sun, Moon, Bell, LogOut, Menu } from 'lucide-vue-next'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'


const auth = useAuthStore()
const router = useRouter()

const user = computed(() => auth.user)
const displayName = computed(() => user.value?.username || 'Usuário')

const displyProfile = computed(() => {
  if (auth.user?.is_superuser) {
    return 'Admin'
  } else if (auth.user?.groups?.length) {
    return auth.user.groups[0]
  } else {
    return 'Visitante' // ou '', ou null, mas NÃO chame logout aqui!
  }
})


// Breadcrumbs simples derivados da rota atual
const route = useRoute()
const breadcrumbs = computed(() => {
  const path = route.path || ''
  const list = [{ label: 'Dashboard', to: '/dashboard' }]
  if (path.startsWith('/network')) {
    list.push({ label: 'Rede', to: '/network' })
    if (path.startsWith('/network/directs')) list.push({ label: 'Diretos' })
    else if (path.startsWith('/network/downlines')) list.push({ label: 'Rede Completa' })
    else if (path.startsWith('/network/adesions')) list.push({ label: 'Adesões' })
    else if (path.startsWith('/network/tree')) list.push({ label: 'Árvore da Rede' })
  } else if (path.startsWith('/licensed')) {
    list.push({ label: 'Licenciados' })
  } else if (path.startsWith('/documents')) {
    list.push({ label: 'Documentos', to: '/documents' })
    if (path.startsWith('/documents/review')) list.push({ label: 'Revisão' })
  } else if (path.startsWith('/reports')) {
    list.push({ label: 'Relatórios', to: '/reports/points' })
    if (path.startsWith('/reports/points')) list.push({ label: 'Pontos' })
    if (path.startsWith('/reports/bonus')) list.push({ label: 'Bônus' })
  }
  return list
})


function logout() {
  auth.logout()
  router.push('/login')
}
</script>
