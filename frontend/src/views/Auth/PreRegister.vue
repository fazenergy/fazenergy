<template>
  <!-- Se autenticado → mostra com sidebar -->
  <div v-if="auth.user" class="flex">
    <Sidebar :mini="false" />
    <div class="flex-1">
      <Header />
      <div class="p-4">
        <FormContent :referrer-username="route.query.ind || ''" />
      </div>
    </div>
  </div>

  <!-- Visitante (sem login) → mostra layout público -->
  <div v-else class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="w-full max-w-4xl bg-white p-8 rounded shadow">
      <FormContent :referrer-username="route.query.ind || ''" />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import Sidebar from '@/components/Sidebar.vue'
import Header from '@/components/Header.vue'
import FormContent from '@/components/FormPreRegister.vue'

const route = useRoute()
const auth = useAuthStore()
</script>
