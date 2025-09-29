<template>
  <div class="space-y-3">
    <div class="flex border-b mb-2 space-x-2">
      <button :class="['px-4 py-2 rounded-t', active==='Config API' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Config API'">API (EndPoint)</button>
      <button :class="['px-4 py-2 rounded-t', active==='Webhook' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Webhook'">Webhook</button>
    </div>
    <div class="bg-white rounded border p-3">
      <h3 class="text-sm font-semibold">Gateway de Pagamento</h3>
      <p class="text-[11px] text-gray-500">Configure aqui o gateway para receber pagamentos na venda de produtos.</p>
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
import { ref, computed, onMounted } from 'vue'
import api from '@/services/axios'
import ConfigApi from './gateway/ConfigApiTab.vue'
import WebhookTab from './gateway/WebhookTab.vue'
import Modal from '@/components/ui/Modal.vue'

// Estado e lógica
const form = ref({ active: true })
const active = ref('Config API')
const saving = ref(false)

const current = computed(() => (active.value === 'Config API' ? ConfigApi : WebhookTab))

async function fetchConfig() {
  try {
    const { data } = await api.get('/api/finance/gateway-config/')
    if (data) form.value = data
  } catch {}
}

async function save() {
  try {
    saving.value = true
    const payload = { ...form.value }
    if (payload.id) {
      await api.put(`/api/finance/gateway-config/${payload.id}/`, payload)
    } else {
      await api.post('/api/finance/gateway-config/', payload)
    }
    showResult(true, 'Configurações do gateway salvas com sucesso.')
  } catch (e) {
    showResult(false, 'Falha ao salvar configurações do gateway.')
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)

// Modal de resultado
const showModal = ref(false)
const modalMessage = ref('')
const modalSuccess = ref(true)
function showResult(success, message){
  modalSuccess.value = !!success
  modalMessage.value = message
  showModal.value = true
}
</script>


