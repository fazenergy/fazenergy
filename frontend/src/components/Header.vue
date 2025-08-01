<!-- src/components/Header.vue -->
<template>
  <header class="flex justify-between items-center px-4 py-2 border-b border-gray-200 text-[80%]">
      <!-- Toggle + título -->
    <div class="flex items-center gap-2">
      <button @click="$emit('toggle-sidebar')" class="hover:text-blue-600">
        <Menu class="w-5 h-5" />
      </button>
      <h1 class="font-semibold">
        Dashboard
      </h1>
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


function logout() {
  auth.logout()
  router.push('/login')
}
</script>
