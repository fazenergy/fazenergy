<template>
  <div class="space-y-3">
    <div class="flex border-b mb-2 space-x-2">
      <button :class="['px-4 py-2 rounded-t', active==='Config API' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Config API'">Config API</button>
      <button :class="['px-4 py-2 rounded-t', active==='Webhook' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Webhook'">Webhook</button>
    </div>
    <component :is="current" :form="form" @save="save" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/axios'
import ConfigApi from './gateway/ConfigApiTab.vue'
import WebhookTab from './gateway/WebhookTab.vue'

// Estado e lógica
const form = ref({ active: true })
const active = ref('Config API')

const current = computed(() => (active.value === 'Config API' ? ConfigApi : WebhookTab))

async function fetchConfig() {
  try {
    const { data } = await api.get('/api/finance/gateway-config/')
    if (data) form.value = data
  } catch {}
}

async function save() {
  const payload = { ...form.value }
  if (payload.id) {
    await api.put(`/api/finance/gateway-config/${payload.id}/`, payload)
  } else {
    await api.post('/api/finance/gateway-config/', payload)
  }
}

onMounted(fetchConfig)
</script>


