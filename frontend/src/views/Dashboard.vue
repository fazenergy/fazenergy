<!-- src/views/Dashboard.vue -->
<!-- src/views/Dashboard.vue -->
<template>
<div class="flex items-center justify-between gap-2">
  <div class="flex items-center gap-2 flex-wrap">
   <!-- ✅ Botão visível para SUPERADMIN -->
    <button
      v-if="isSuperadmin || isLicensed"
      @click="showNew = true"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 inline-flex items-center gap-2"
    >
      <Plus class="w-4 h-4" />
      Cadastrar Licenciado
    </button>
    <button
      v-if="isLicensed || isSuperadmin"
      @click="openInvite"
      class="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 inline-flex items-center gap-2"
    >
      <Share2 class="w-4 h-4" />
      Convidar Licenciado
    </button>

    <!-- Exportar / Imprimir -->
    <button
      @click="exportDashboard"
      class="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 inline-flex items-center gap-2"
    >
      <FileDown class="w-4 h-4" />
      Exportar
    </button>
    <button
      @click="printDashboard"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 inline-flex items-center gap-2"
    >
      <Printer class="w-4 h-4" />
      Imprimir
    </button>
  </div>

  <!-- Indicador de status do cadastro (lado direito) -->
  <div v-if="isLicensed && licensedStatus" class="ml-auto">
    <div :class="'px-3 py-1.5 rounded border shadow-sm inline-flex items-center gap-2 '+ licensedStatus.class">
      <component :is="licensedStatus.icon" class="w-4 h-4" />
      <span class="text-sm font-medium">Cadastro: {{ licensedStatus.label }}</span>
    </div>
  </div>

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
      <FormPreRegister :key="preFormKey" ref="preForm" :in-modal="true" @close="showNew=false" @completed="preFormCompleted=true" />
      <template #footer>
        <div class="flex items-center justify-end gap-2 py-2">
          <button class="px-4 py-2 rounded border" @click="showNew=false">Fechar</button>
          <button form="preRegisterForm" type="submit" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">Gravar</button>
        </div>
      </template>
    </Modal>
</div>
<div class="flex">
    <div class="flex-1">
    <main ref="dashboardRef" class="pt-6 pr-6 pb-6 pl-0 space-y-6">
    
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
         <template #icon><component :is="iconFor(c)" class="w-7 h-7" /></template>
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
import { computed, ref, onMounted, watch } from 'vue'
import Card from '@/components/ui/Card.vue'
import { UserPlus, DollarSign, TrendingUp, Users, FileText, Plus, Share2, FileDown, Printer, CheckCircle2, Clock, XCircle, AlertTriangle } from 'lucide-vue-next'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import FormPreRegister from '@/components/FormPreRegister.vue'

const auth = useAuthStore()
const router = useRouter()
const showNew = ref(false)
const preForm = ref(null)
const preFormKey = ref(0)
const dashboardRef = ref(null)
const preFormCompleted = ref(false)

// Exemplo: se você salva grupos no `auth.user`
const isLicensed = computed(() => auth.user?.groups?.includes('Licenciado'))
const isSuperadmin = computed(() => auth.user?.is_superuser || auth.user?.groups?.includes('Superadmin'))

// abre modal de cadastro pelo botão acima (showNew=true)

const cards = ref([])
const quickActions = ref([])
const billing = ref({ pending_annual_payment: false, payment_link_url: null, adesion_id: null })
const documents = ref({ pending: false, status: 'pending' })
const summary = ref({ pre_registers: 0, activations: 0, withdraw_requests: 0 })

// Mapeia status do cadastro/licença do usuário
const licensedStatus = computed(() => {
  // Preferência: status vindo do dashboard -> documents.status
  const st = (documents.value?.status || '').toLowerCase()
  // Fallback simples por enquanto: se não houver status, mostra pendente quando houver documentos pendentes ou pagamento pendente
  if (st === 'approved' || st === 'ativo' || st === 'active') {
    return { label: 'Ativo', class: 'bg-emerald-50 border-emerald-200 text-emerald-700', icon: CheckCircle2 }
  }
  if (st === 'pending' || st === 'aguardando' || documents.value?.pending) {
    return { label: 'Em validação', class: 'bg-blue-50 border-blue-200 text-blue-700', icon: Clock }
  }
  if (st === 'rejected' || st === 'reprovado') {
    return { label: 'Reprovado', class: 'bg-red-50 border-red-200 text-red-700', icon: XCircle }
  }
  if (billing.value?.pending_annual_payment) {
    return { label: 'Pagamento pendente', class: 'bg-amber-50 border-amber-200 text-amber-700', icon: AlertTriangle }
  }
  return { label: 'Em validação', class: 'bg-blue-50 border-blue-200 text-blue-700', icon: Clock }
})

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

function iconFor(card) {
  const key = card?.key
  switch (key) {
    case 'directs':
      return UserPlus
    case 'team_size':
      return Users
    case 'career':
      return TrendingUp
    case 'docs_status':
      return FileText
    case 'operator_paid_adesions':
      return DollarSign
    case 'operator_paid_plants':
      return Users
    case 'operator_bonus_total':
      return DollarSign
    default:
      return Users
  }
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
    // Oculta imediatamente o botão até receber o evento completed
    preFormCompleted.value = true
  } catch {}
}

// mantém comportamento simples: usamos submit do form

// Sempre resetar o formulário ao abrir o modal
watch(showNew, (val) => {
  if (val && preForm.value && preForm.value.resetForm) {
    preForm.value.resetForm()
  }
  if (val) {
    // força recriar o componente evitando preenchimento automático do navegador
    preFormKey.value++
    // tentativa adicional: limpa inputs email/senha após montar
    const clear = () => {
      const formEl = document.getElementById('preRegisterForm')
      if (!formEl) return
      formEl.querySelectorAll('#pre_email, #pre_password, #pre_confirm_password').forEach((el) => {
        try {
          // @ts-ignore
          el.value = ''
          el.dispatchEvent(new Event('input', { bubbles: true }))
        } catch {}
      })
    }
    setTimeout(clear, 0)
    setTimeout(clear, 100)
    setTimeout(clear, 300)
    preFormCompleted.value = false
  }
})

// Export/Print Dashboard
async function exportDashboard() {
  try {
    const el = dashboardRef.value
    if (!el) return
    const { default: html2canvas } = await import('html2canvas')
    const { jsPDF } = await import('jspdf')
    const canvas = await html2canvas(el, { scale: 2, useCORS: true })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pageWidth
    const imgHeight = canvas.height * imgWidth / canvas.width
    let y = 0
    // Suporte a múltiplas páginas
    while (y < imgHeight) {
      pdf.addImage(imgData, 'PNG', 0, -y, imgWidth, imgHeight)
      y += pageHeight
      if (y < imgHeight) pdf.addPage()
    }
    pdf.save(`dashboard_${new Date().toISOString().slice(0,10)}.pdf`)
  } catch {}
}

async function printDashboard() {
  try {
    const el = dashboardRef.value
    if (!el) return
    const { default: html2canvas } = await import('html2canvas')
    const canvas = await html2canvas(el, { scale: 2, useCORS: true })
    const dataUrl = canvas.toDataURL('image/png')
    const win = window.open('', '_blank')
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
      <title>Imprimir Dashboard</title>
      <style>body{margin:0} img{display:block; width:100%; height:auto}</style>
    </head><body onload="window.print(); setTimeout(()=>window.close(), 50)">
      <img src="${dataUrl}" />
    </body></html>`
    win.document.write(html)
    win.document.close()
  } catch {}
}
</script>
