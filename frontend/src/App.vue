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
      <Header @toggle-sidebar="toggleSidebar" @toggle-theme="toggleTheme" />
      
      <main class="p-4">
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
import { computed, ref, onMounted  } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'

const showSidebar = ref(true)
const route = useRoute()

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
})

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  setTheme()
}

function setTheme() {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}



</script>
