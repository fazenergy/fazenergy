<!-- src/components/AlertsPanel.vue -->
<template>
  <div class="space-y-2">
    <!-- Contrato pendente -->
    <div v-if="subscription.contract_status && subscription.contract_status !== 'signed'" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
        <div>
          <div class="font-semibold text-amber-800">Contrato de adesão pendente.</div>
          <div class="text-amber-800/80 text-sm">Reenvie o contrato para seu e‑mail para assinar eletronicamente.</div>
        </div>
      </div>
      <div>
        <button @click="resendContract" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Reenviar Contrato</button>
      </div>
    </div>

    <!-- Documentos PF -->
    <div v-if="isLicensed && documents && documents.pf && documents.pf !== 'approved'" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
        <div>
          <div class="font-semibold text-amber-800">Atenção: você ainda não concluiu o envio de sua documentação pessoal.</div>
          <div class="text-amber-800/80 text-sm">Conclua o envio e aguarde aprovação para ativação completa.</div>
        </div>
      </div>
      <div>
        <button @click="router.push('/documents')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Enviar Documentos</button>
      </div>
    </div>

    <!-- Documentos PJ -->
    <div v-if="isLicensed && documents && Array.isArray(documents.company_cnpjs) && documents.company_cnpjs.length && documents.pj && documents.pj !== 'approved'" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
        <div>
          <div class="font-semibold text-amber-800">Você ainda não enviou sua documentação referente à sua empresa de CNPJ {{ maskCnpj(documents.company_cnpjs[0]) }}.</div>
          <div class="text-amber-800/80 text-sm">Anexe os documentos obrigatórios para aprovação.</div>
        </div>
      </div>
      <div>
        <button @click="router.push('/company')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Enviar Documentos</button>
      </div>
    </div>

    <!-- Pagamento pendente -->
    <div v-if="billing.pending_annual_payment" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
        <div>
          <div class="font-semibold text-amber-800">Pagamento do Plano Anual pendente</div>
          <div class="text-amber-800/80 text-sm">Conclua o pagamento para ativar e manter seus benefícios na rede.</div>
        </div>
      </div>
      <div>
        <button @click="openPayment" class="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Pagar Agora</button>
      </div>
    </div>

    <!-- Operador: documentos pendentes -->
    <div v-if="isOperator && pendingDocumentsCount > 0" class="p-4 bg-blue-50 border border-blue-200 rounded flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></div>
        <div>
          <div class="font-semibold text-blue-800">
            {{ pendingDocumentsCount }} {{ pendingDocumentsCount === 1 ? 'documento' : 'documentos' }} pendente{{ pendingDocumentsCount === 1 ? '' : 's' }} de revisão
          </div>
          <div class="text-blue-800/80 text-sm">Há documentos de licenciados aguardando sua revisão e aprovação.</div>
        </div>
      </div>
      <div>
        <button @click="router.push('/documents/review')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Revisar Documentos</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/services/axios'

const router = useRouter()
const auth = useAuthStore()

const isLicensed = computed(() => auth.user?.groups?.includes('Licenciado'))
const isOperator = computed(() => auth.user?.groups?.includes('Operador') || auth.user?.is_staff || auth.user?.is_superuser)

const documents = ref({})
const billing = ref({ pending_annual_payment: false })
const subscription = ref({ contract_status: 'pending' })
const pendingDocumentsCount = ref(0)

async function fetchAlerts() {
  try {
    const { data } = await api.get('/api/core/dashboard/')
    documents.value = data?.documents || {}
    billing.value = data?.billing || { pending_annual_payment: false }
    subscription.value = data?.subscription || { contract_status: 'pending' }
  } catch (e) {
    documents.value = {}
    billing.value = { pending_annual_payment: false }
    subscription.value = { contract_status: 'pending' }
  }
  if (isOperator.value) {
    try {
      const { data: countData } = await api.get('/api/core/pending-documents-count/')
      pendingDocumentsCount.value = countData?.count || 0
    } catch {
      pendingDocumentsCount.value = 0
    }
  }
}

onMounted(fetchAlerts)

function maskCnpj(v) {
  try {
    const s = String(v || '').padStart(14, '0').slice(-14)
    return `${s.slice(0,2)}.${s.slice(2,5)}.${s.slice(5,8)}/${s.slice(8,12)}-${s.slice(12,14)}`
  } catch { return v }
}

function openPayment() {
  const adesionId = billing.value?.adesion_id
  if (!adesionId) return router.push('/network/adesions')
  router.push({ path: '/payment', query: { adesion: adesionId } })
}

async function resendContract() {
  try {
    await api.post('/api/contracts/templates/resend-adesion/')
    // Silencioso no componente; o Dashboard já mostra feedback quando necessário
  } catch {}
}
</script>


