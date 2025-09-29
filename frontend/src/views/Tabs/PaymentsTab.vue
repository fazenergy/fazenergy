<template>
  <div class="space-y-3">
    <!-- Tabs locais (pagamentos) -->
    <div class="flex border-b mb-2 space-x-2">
      <button :class="['px-4 py-2 rounded-t', active==='Configurações' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Configurações'">Configurações</button>
      <button :class="['px-4 py-2 rounded-t', active==='Config API' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Config API'">API (End Point)</button>
      <button :class="['px-4 py-2 rounded-t', active==='Webhook' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Webhook'">Webhook</button>
    </div>
    <component :is="current" :form="form" :saving="saving" @save="save" />
    <!-- Modal de feedback -->
    <Modal v-model="showModal" :header-blue="modalSuccess" :no-header-border="false" max-width="max-w-md">
      <template #title>{{ modalSuccess ? 'Sucesso' : 'Erro' }}</template>
      <div class="text-sm" :class="modalSuccess ? 'text-emerald-700' : 'text-rose-700'">{{ modalMessage }}</div>
      <template #footer>
        <div class="flex items-center justify-end gap-2">
          <button class="px-3 py-1.5 rounded border" @click="showModal=false">Fechar</button>
        </div>
      </template>
    </Modal>
  </div>
  </template>

<script setup>
// Abas internas de Pagamentos: Configurações gerais, Config API e Webhook
import { ref, computed, onMounted } from 'vue'
import SettingsTab from './payments/SettingsTab.vue'
import ConfigApi from './payments/ConfigApiTab.vue'
import WebhookTab from './payments/WebhookTab.vue'
import api from '@/services/axios'
import { useSettingsStore } from '@/store/settings'

const active = ref('Configurações')
const form = ref({ active: true })
const saving = ref(false)
const settingsStore = useSettingsStore()

const current = computed(() => {
  if (active.value === 'Config API') return ConfigApi
  if (active.value === 'Webhook') return WebhookTab
  return SettingsTab
})

async function fetchConfig() {
  try {
    const { data } = await api.get('/api/finance/pix-config/')
    if (data) form.value = data
  } catch {}
}

async function save(payloadFromChild) {
  try {
    saving.value = true
    // Pode receber payload vindo da sub-aba Configurações
    if (payloadFromChild && active.value === 'Configurações') {
      // Persistência local das regras de saque
      settingsStore.setPayments({ ...payloadFromChild })
      settingsStore.saveToStorage()
    }
    const payload = { ...form.value }
    if (payload.id) {
      await api.patch(`/api/finance/pix-config/${payload.id}/`, payload)
    } else {
      await api.post('/api/finance/pix-config/', payload)
    }
    showResult(true, 'Configurações salvas com sucesso.')
  } catch (e) {
    showResult(false, 'Falha ao salvar configurações. Verifique os campos e tente novamente.')
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)

// Modal de resultado
import Modal from '@/components/ui/Modal.vue'
const showModal = ref(false)
const modalMessage = ref('')
const modalSuccess = ref(true)
function showResult(success, message){
  modalSuccess.value = !!success
  modalMessage.value = message
  showModal.value = true
}
</script>

