<!-- src/App.vue -->
<template>
  <div v-if="!isAuthRoute" class="flex min-h-screen">
    <!-- Sidebar -->
    <div
      :class="[
        'transition-all duration-300',
        showSidebar ? 'w-52' : 'w-16'
      ]"
      class="bg-[#1d4ed8]"
    >
      <Sidebar :mini="!showSidebar" />
    </div>

      <!-- Conteúdo principal -->
    <div class="flex-1 flex flex-col">
      <Header @toggle-sidebar="toggleSidebar" @toggle-theme="toggleTheme" :alerts-count="globalAlertsCount" @open-alerts="openGlobalAlerts" />
      <!-- Modal Global de Alertas -->
      <div v-if="showGlobalAlerts" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/30" @click="showGlobalAlerts=false"></div>
        <div class="relative bg-white w-[720px] max-w-[95vw] rounded-lg shadow-lg">
          <div class="px-4 py-2 border-b font-semibold">Mensagens Importantes</div>
          <div class="p-4 max-h-[70vh] overflow-auto space-y-3">
            <AlertsPanel />
          </div>
          <div class="px-4 py-2 border-t flex justify-end">
            <button class="px-4 py-2 rounded border text-sm" @click="showGlobalAlerts=false">Fechar</button>
          </div>
        </div>
      </div>
      
      <main class="p-4 text-[0.9rem]">
        <router-view />
      </main>
    </div>
  </div>

  <!-- Renderiza login/preRegister sozinhos -->
  <div v-else>
    <router-view />
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import { useSettingsStore } from '@/store/settings'
import { useAuthStore } from '@/store/auth'
import AlertsPanel from '@/components/AlertsPanel.vue'

const showSidebar = ref(true)
const route = useRoute()
const auth = useAuthStore()
const showGlobalAlerts = ref(false)
const globalAlertsCount = ref(0)

const isAuthRoute = computed(() => {
  return ['/login', '/preRegister'].includes(route.path)
})

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}


// TEMA DARKLIGHT
const isDark = ref(false)

onMounted(() => {
  // Se tiver salvo no localStorage, aplica. Senão mantém claro.
  if (localStorage.getItem('theme') === 'dark') {
    isDark.value = true
  }
  setTheme()
  // Inicializa favicon baseado nas configs
  applyFavicon()
  // Sincroniza contador do Dashboard via localStorage
  try {
    const n = Number(localStorage.getItem('alertsCount') || '0')
    if (!Number.isNaN(n)) globalAlertsCount.value = n
  } catch {}
})

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  setTheme()
}

// Exemplo simples: deixa o contador como 0 aqui; dashboard pode emitir via eventBus/localStorage
function openGlobalAlerts() {
  showGlobalAlerts.value = true
}

function setTheme() {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// =====================
// FAVICON DINÂMICO
// =====================
const settingsStore = useSettingsStore()
settingsStore.loadFromStorage()

// Observa mudanças futuras no store (caso salve sem recarregar)
watch(() => settingsStore.settings.general.favicon_data_url, () => applyFavicon())

function applyFavicon() {
  try {
    const href = settingsStore.settings.general.favicon_data_url
    // Garante um <link rel="icon"> no head
    let link = document.querySelector("link[rel='icon']") || document.createElement('link')
    link.setAttribute('rel', 'icon')
    link.setAttribute('type', 'image/png')
    link.setAttribute('href', href || '/favicon.ico')
    if (!link.parentNode) document.head.appendChild(link)
  } catch (e) { /* noop */ }
}

// Observa alterações no localStorage do contador
window.addEventListener('storage', (e) => {
  if (e.key === 'alertsCount') {
    const n = Number(e.newValue || '0')
    if (!Number.isNaN(n)) globalAlertsCount.value = n
  }
})



</script>
