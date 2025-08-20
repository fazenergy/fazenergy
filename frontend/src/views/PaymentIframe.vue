<template>
  <div class="min-h-screen flex flex-col">
    <div class="p-3 bg-white border-b flex items-center justify-between">
      <div class="text-sm text-gray-700">Pagamento do Plano Anual</div>
      <div class="text-xs" :class="statusClass">Status: {{ statusLabel }}</div>
    </div>

    <div class="flex-1 grid overflow-hidden">
      <iframe v-if="paymentUrl" :src="paymentUrl" class="block" :style="iframeStyle"></iframe>
      <div v-else class="grid place-items-center text-gray-500">Carregando link de pagamento...</div>
    </div>

    <div class="p-3 bg-white border-t flex items-center justify-end gap-2">
      <button @click="refreshNow" class="px-3 py-1.5 border rounded">Atualizar Status</button>
      <button v-if="isFinished" @click="goDashboard" class="px-3 py-1.5 rounded bg-blue-600 text-white">Voltar ao Dashboard</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/axios'

const route = useRoute()
const router = useRouter()

const adesionId = computed(() => route.query.adesion)
const licensedUsername = computed(() => route.query.licensed)
const paymentUrl = ref('')
const paymentStatus = ref('pending')
const loading = ref(false)
let timer = null

const statusLabel = computed(() => ({
  pending: 'Pendente',
  paid: 'Pago',
  authorized: 'Autorizado',
  canceled: 'Cancelado',
  failed: 'Falhou',
  refunded: 'Estornado'
}[paymentStatus.value] || paymentStatus.value))

const statusClass = computed(() => {
  switch (paymentStatus.value) {
    case 'paid':
    case 'authorized':
      return 'text-emerald-700'
    case 'failed':
    case 'canceled':
      return 'text-rose-700'
    default:
      return 'text-amber-700'
  }
})

const isFinished = computed(() => ['paid', 'authorized', 'failed', 'canceled', 'refunded'].includes(paymentStatus.value))

// Estilo do iframe com zoom 85%
const iframeStyle = computed(() => ({
  width: '118%',
  height: '118%',
  border: '0',
  transform: 'scale(0.85)',
  transformOrigin: '0 0',
}))

async function fetchLatestLink() {
  if (!adesionId.value && !licensedUsername.value) return
  const qs = adesionId.value ? `adesion=${adesionId.value}` : `licensed_username=${encodeURIComponent(licensedUsername.value)}`
  const { data } = await api.get(`/api/finance/payment-links/latest/?${qs}`)
  const latest = data
  if (latest) {
    paymentUrl.value = latest.url
    paymentStatus.value = latest.status
  }
}

async function refreshStatus() {
  if (!adesionId.value && !licensedUsername.value) return
  const qs = adesionId.value ? `adesion=${adesionId.value}` : `licensed_username=${encodeURIComponent(licensedUsername.value)}`
  const { data } = await api.get(`/api/finance/payment-links/latest/?${qs}`)
  const latest = data
  if (latest) {
    paymentStatus.value = latest.status
  }
  if (isFinished.value) stopPolling()
}

function startPolling() {
  stopPolling()
  timer = setInterval(refreshStatus, 3500)
}
function stopPolling() {
  if (timer) { clearInterval(timer); timer = null }
}

function refreshNow() { refreshStatus() }
function goDashboard() { router.push('/dashboard') }

onMounted(async () => {
  loading.value = true
  try {
    await fetchLatestLink()
    startPolling()
  } finally {
    loading.value = false
  }
})
onUnmounted(stopPolling)
</script>


