<template>
  <!-- Se autenticado e não embed → mostra com sidebar -->
  <div v-if="isAuthenticated && !isEmbed" class="min-h-screen flex">
    <Sidebar :mini="mini" />
    <div class="flex-1 flex flex-col min-h-screen">
      <Header @toggle-sidebar="mini = !mini" />
      <div class="p-4 flex-1 bg-white">
        <FormContent :referrer-username="referrerQuery" />
      </div>
    </div>
  </div>

  <!-- Demais casos (visitante ou embed) → layout público/embutido -->
  <div v-else class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="w-full max-w-4xl bg-white p-8 rounded shadow">
      <FormContent :referrer-username="referrerQuery" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import Sidebar from '@/components/Sidebar.vue'
import Header from '@/components/Header.vue'
import FormContent from '@/components/FormPreRegister.vue'

const route = useRoute()
const auth = useAuthStore()
const isAuthenticated = computed(() => !!auth.user)
const isEmbed = computed(() => String(route.query.embed || '').toLowerCase() === '1' || String(route.query.embed || '').toLowerCase() === 'true')
const referrerQuery = computed(() => String(route.query.ind || route.query.indicador || ''))
const mini = ref(false)

// Se houver token mas user ainda não carregado, tenta buscar o perfil para evitar tela em branco
if (!auth.user && localStorage.getItem('accessToken')) {
  auth.fetchProfile().catch(() => {})
}
</script>
