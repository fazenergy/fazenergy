<!-- src/views/Dashboard.vue -->
<!-- src/views/Dashboard.vue -->
<template>
<div class="flex items-center gap-2">
   <!-- ✅ Botão visível para SUPERADMIN -->
    <button
      v-if="isSuperadmin"
      @click="showNew = true"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 inline-flex items-center gap-2"
    >
      <Plus class="w-4 h-4" />
      Cadastrar Licenciado
    </button>
    <button
      v-if="isLicensed"
      @click="openInvite"
      class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 inline-flex items-center gap-2"
    >
      <Share2 class="w-4 h-4" />
      Convidar Licenciado
    </button>

    <!-- Modal de Convite -->
    <Modal v-model="showInvite" :header-blue="true" :no-header-border="true">
      <template #title>Convidar Licenciado</template>
      <div class="space-y-4">
        <div class="text-sm text-gray-700">
          Compartilhe o link de cadastro com seu indicado. Escolha o canal abaixo.
        </div>
        <div class="flex items-center gap-4">
          <label class="inline-flex items-center gap-2 text-sm">
            <input type="radio" value="whatsapp" v-model="inviteChannel" /> WhatsApp
          </label>
          <label class="inline-flex items-center gap-2 text-sm">
            <input type="radio" value="email" v-model="inviteChannel" /> E-mail
          </label>
        </div>

        <div v-if="inviteChannel==='email'" class="flex items-center gap-2">
          <input v-model.trim="inviteEmail" type="email" placeholder="email@exemplo.com" class="flex-1 border rounded px-3 py-2 text-sm" />
          <button @click="sendInviteEmail" :disabled="!inviteEmail" class="px-3 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm disabled:opacity-50">Enviar</button>
        </div>

        <div v-else class="flex items-center gap-2">
          <button @click="shareWhatsApp" class="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Compartilhar no WhatsApp</button>
        </div>

        <div class="text-xs text-gray-500">
          Link: <span class="underline break-all">{{ inviteLink }}</span>
        </div>
      </div>
    </Modal>
    <!-- Modal de Cadastro -->
    <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
      <template #title>Novo Licenciado</template>
      <FormPreRegister ref="preForm" :in-modal="true" @close="showNew=false" />
      <template #footer>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 rounded border" @click="showNew=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white" @click="submitPreForm">Gravar</button>
        </div>
      </template>
    </Modal>
</div>
<div class="flex">
    <div class="flex-1">
    <main class="p-6 space-y-6">
    
    <!-- Alert/Banner de documentos pendentes -->
    <div v-if="isLicensed && documents?.pending" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-start gap-3">
        <div class="mt-0.5 w-2 h-2 rounded-full bg-amber-500"></div>
        <div>
          <div class="font-semibold text-amber-800">Você ainda não enviou seus documentos de licenciado para validação</div>
          <div class="text-amber-800/80 text-sm">Envie seus documentos para prosseguir com a validação.</div>
        </div>
      </div>
      <div>
        <button @click="router.push('/documents')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Enviar Documentos</button>
      </div>
    </div>

    <!-- Alert/Banner de pagamento pendente -->
    <div v-if="billing.pending_annual_payment" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-start gap-3">
        <div class="mt-0.5 w-2 h-2 rounded-full bg-amber-500"></div>
        <div>
          <div class="font-semibold text-amber-800">Pagamento do Plano Anual pendente</div>
          <div class="text-amber-800/80 text-sm">Conclua o pagamento para ativar e manter seus benefícios na rede.</div>
        </div>
      </div>
      <div>
        <button @click="openPayment" class="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Pagar Agora</button>
      </div>
    </div>

    <!-- Cards principais -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card v-for="(c, idx) in cards" :key="c.key" :className="cardClass(c, idx)" @click="c.route && router.push(c.route)" class="cursor-pointer">
         <template #title><div>{{ c.title }}</div></template>
         <template #content><div><p class="text-2xl font-bold">{{ c.value }}</p></div></template>
         <template #description><div v-if="c.delta">{{ c.delta }}</div></template>
         <template #icon><UserPlus class="w-5 h-5" /></template>
      </Card>
    </div>

  <!-- Ações rápidas, relatórios e configurações -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Ações Rápidas</h2>
            <button v-for="qa in quickActions" :key="qa.route" @click="router.push(qa.route)" class="block w-full p-2 bg-blue-500 text-white rounded mb-2">{{ qa.label }}</button>
          </div>

          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Relatórios</h2>
            <p>Relatórios aqui...</p>
          </div>

          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Configurações</h2>
            <p>Configurações aqui...</p>
          </div>
        </div>

        <div class="border p-4 rounded">
          <h2 class="font-bold mb-2">Resumo Operacional</h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            <div class="p-3 rounded bg-gray-50 border">
              <div class="text-gray-500">Pré-Cadastros (30 dias)</div>
              <div class="text-2xl font-bold">{{ summary.pre_registers || 0 }}</div>
            </div>
            <div class="p-3 rounded bg-gray-50 border">
              <div class="text-gray-500">Ativações</div>
              <div class="text-2xl font-bold">{{ summary.activations || 0 }}</div>
            </div>
            <div class="p-3 rounded bg-gray-50 border">
              <div class="text-gray-500">Solicitações de Saque</div>
              <div class="text-2xl font-bold">{{ summary.withdraw_requests || 0 }}</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
  
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { computed, ref, onMounted } from 'vue'
import Card from '@/components/ui/Card.vue'
import { UserPlus, DollarSign, TrendingUp, UserCheck, Plus, Share2 } from 'lucide-vue-next'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'
import FormPreRegister from '@/components/FormPreRegister.vue'

const auth = useAuthStore()
const router = useRouter()
const showNew = ref(false)
const preForm = ref(null)

// Exemplo: se você salva grupos no `auth.user`
const isLicensed = computed(() => auth.user?.groups?.includes('Licenciado'))
const isSuperadmin = computed(() => auth.user?.is_superuser || auth.user?.groups?.includes('Superadmin'))

// abre modal de cadastro pelo botão acima (showNew=true)

const cards = ref([])
const quickActions = ref([])
const billing = ref({ pending_annual_payment: false, payment_link_url: null, adesion_id: null })
const documents = ref({ pending: false, status: 'pending' })
const summary = ref({ pre_registers: 0, activations: 0, withdraw_requests: 0 })

async function fetchDashboard() {
  const { data } = await api.get('/api/core/dashboard/')
  cards.value = data?.cards || []
  quickActions.value = data?.quickActions || []
  billing.value = data?.billing || { pending_annual_payment: false }
  documents.value = data?.documents || { pending: false, status: 'pending' }
  summary.value = data?.summary || { pre_registers: 0, activations: 0, withdraw_requests: 0 }
}

onMounted(fetchDashboard)

function cardClass(card, index) {
  const base = 'bg-gradient-to-r text-white shadow-lg hover:scale-[1.01] transition-transform'
  const byKey = {
    total_licensed: 'from-blue-500 to-blue-600',
    active_affiliates: 'from-emerald-500 to-emerald-600',
    roots_count: 'from-purple-500 to-purple-600',
    network_edges: 'from-orange-500 to-orange-600',
    directs: 'from-blue-500 to-blue-600',
    team_size: 'from-purple-500 to-purple-600',
    active_team: 'from-emerald-500 to-emerald-600',
    career: 'from-orange-500 to-orange-600',
    docs_status: 'from-amber-400 to-orange-500',
    operator_paid_adesions: 'from-emerald-600 to-emerald-700',
    operator_paid_plants: 'from-blue-500 to-blue-600',
    operator_bonus_total: 'from-purple-600 to-purple-700',
    operator_points_total: 'from-orange-600 to-orange-700',
  }
  const palette = [
    'from-blue-500 to-blue-600',
    'from-emerald-500 to-emerald-600',
    'from-purple-500 to-purple-600',
    'from-orange-500 to-orange-600',
  ]
  const grad = byKey[card?.key] || palette[index % palette.length]
  return `${base} ${grad}`
}

function openPayment() {
  const adesionId = billing.value?.adesion_id
  if (!adesionId) return router.push('/network/adesions')
  router.push({ path: '/payment', query: { adesion: adesionId } })
}

// Convite de licenciado
const showInvite = ref(false)
const inviteChannel = ref('whatsapp')
const inviteEmail = ref('')
const inviteLink = computed(() => {
  const origin = window.location.origin
  const username = auth.user?.username || ''
  return `${origin}/preRegister?ind=${encodeURIComponent(username)}`
})

function openInvite() {
  inviteChannel.value = 'whatsapp'
  inviteEmail.value = ''
  showInvite.value = true
}

function shareWhatsApp() {
  const text = `Olá! Segue meu link para se cadastrar na FazEnergy: ${inviteLink.value}`
  if (navigator.share) {
    navigator.share({ title: 'Convite FazEnergy', text, url: inviteLink.value }).catch(()=>{})
  } else {
    const url = `https://wa.me/?text=${encodeURIComponent(text)}`
    window.open(url, '_blank')
  }
}

function sendInviteEmail() {
  const subject = 'Convite para cadastro na FazEnergy'
  const body = `Olá!\n\nUse este link para se cadastrar: ${inviteLink.value}\n\nObrigado!`
  const mail = `mailto:${encodeURIComponent(inviteEmail.value)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  window.location.href = mail
}

function submitPreForm() {
  try {
    const formEl = document.getElementById('preRegisterForm')
    if (formEl && typeof formEl.requestSubmit === 'function') {
      formEl.requestSubmit()
    } else if (formEl) {
      formEl.submit()
    }
  } catch {}
}
</script>
