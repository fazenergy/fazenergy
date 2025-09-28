<template>
  <!-- Toolbar padrão de relatórios -->
  <div class="mb-3 bg-white rounded">
    <div class="flex items-center gap-2 flex-wrap">
      <!-- Solicitar Saque (Licenciado) - primeiro da barra -->
      <button v-if="isLicensed" @click="openWithdraw" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <DollarSign class="w-4 h-4" />
        <span>Solicitar Saque</span>
      </button>
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <FileDown class="w-4 h-4" />
        <span>Exportar</span>
      </button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <Printer class="w-4 h-4" />
        <span>Imprimir</span>
      </button>

      <!-- Info regras de saque (sempre antes do filtro, após Imprimir) -->
      <button @click="showWithdrawRules=true" class="inline-flex items-center justify-center w-8 h-8 text-blue-600 hover:text-blue-700 border border-blue-200 hover:border-blue-300" title="Regras de Saque">
        <Info class="w-4 h-4" />
      </button>

      <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
        <input v-model.trim="search" type="text" placeholder="Pesquisar..."
               class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
        <button @click="applySearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 hover:bg-blue-700 text-white" title="Pesquisar">
          <Search class="w-4 h-4" />
        </button>
        <button @click="clearSearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 text-gray-700" title="Limpar">
          <Eraser class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>

  <div ref="gridWrapper">
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight" :show-actions="false">
      <template #title>Relatório de Fechamentos</template>
      <template #col:amount_paid="{ row }">{{ formatNumber(row.amount_paid) }}</template>
      <template #col:amount_unpaid="{ row }">{{ formatNumber(row.amount_unpaid) }}</template>
    </DataTable>
  </div>

  <!-- Modais -->
  <Modal v-model="showWithdrawRules" :header-blue="true" :no-header-border="true">
    <template #title>Regras para Saque</template>
    <div class="space-y-2 text-sm text-gray-700">
      <div>Valor mínimo para saque: R$ {{ minWithdraw.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
      <div>Dias liberados para solicitar saque: {{ withdrawDays }}</div>
      <div>Solicitando hoje, previsão de pagamento: {{ payoutProjection }}</div>
      <div>Taxa por solicitação: R$ {{ feeFixed.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
      <div>Todos os impostos devidos serão recolhidos na fonte e descontados no saque.</div>
      <div>Se existir solicitação em aberto, não é possível abrir nova até processamento.</div>
    </div>
  </Modal>

  <Modal v-model="showWithdraw" :header-blue="true" :no-header-border="true">
    <template #title>Solicitar Saque</template>
    <div class="space-y-3 text-sm">
      <div class="text-gray-700">Selecione sua conta cadastrada para receber o pagamento:</div>
      <select v-model="selectedBank" class="w-full border rounded px-2 py-1 h-8">
        <option :value="null">Selecione</option>
        <option v-for="b in bankAccounts" :key="b.id" :value="b.id">
          {{ b.bank_code }} - {{ b.bank_name || 'Banco' }} | Agência {{ b.agency_number }}-{{ b.agency_digit }} | Conta {{ b.account_number }}-{{ b.account_digit }} ({{ b.owner_type==='pj' ? 'PJ' : 'PF' }})
        </option>
      </select>

      <div v-if="selectedBank">
        <!-- Preenchimento automático bloqueado -->
        <div class="grid grid-cols-2 gap-2">
          <input :value="displaySelected('bank')" disabled class="border rounded px-2 py-1 h-8 bg-gray-100" />
          <input :value="displaySelected('type')" disabled class="border rounded px-2 py-1 h-8 bg-gray-100" />
          <input :value="displaySelected('agency')" disabled class="border rounded px-2 py-1 h-8 bg-gray-100" />
          <input :value="displaySelected('account')" disabled class="border rounded px-2 py-1 h-8 bg-gray-100" />
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 items-end">
        <div>
          <label class="block text-xs text-gray-600 mb-1">Saldo disponível</label>
        <div class="h-12 rounded-lg border border-emerald-200 bg-emerald-50 px-3 flex items-center justify-between">
          <div class="text-xl font-bold text-emerald-700">{{ formatCurrencyBRL(balanceAvailable) }}</div>
        </div>
        </div>
        <div>
          <label class="block text-xs text-gray-600 mb-1">Valor do Saque</label>
          <input
            :value="withdrawAmountDisplay"
            @input="onAmountInput"
            inputmode="decimal"
            class="border rounded px-3 py-2 h-12 text-lg w-full"
            :placeholder="`Até ${balanceAvailable.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`"
          />
        </div>
      </div>

      <div class="text-xs text-gray-600">
        Ao confirmar, será cobrada taxa de R$ {{ feeFixed.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}. Impostos serão retidos na fonte.
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2 py-2">
        <button class="px-4 py-2 rounded border" @click="showWithdraw=false">Fechar</button>
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-60" @click="submitWithdraw" :disabled="submitting">Confirmar</button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'
import { FileDown, Printer, Search, Eraser, Info, DollarSign } from 'lucide-vue-next'
import Modal from '@/components/ui/Modal.vue'
import { useAuthStore } from '@/store/auth'

const rows = ref([])
const loading = ref(false)
const submitting = ref(false)
const showWithdraw = ref(false)
const showWithdrawRules = ref(false)
const bankAccounts = ref([])
const selectedBank = ref(null)
// Valor do saque (display e valor numérico em paralelo para máscara estável)
const withdrawAmountDisplay = ref('')
const withdrawAmountValue = ref(0)
const hasPendingWithdraw = ref(false)
const balanceAvailable = ref(0)
const minWithdraw = ref(50)
const feeFixed = ref(10)
const withdrawDays = ref('Seg, Qua e Sex')
const payoutProjection = ref('próximo dia útil')
const auth = useAuthStore()
const isLicensed = computed(() => auth.user?.groups?.includes('Licenciado'))

const search = ref('')

// Máscara BRL baseada em dígitos (centavos): estável enquanto digita
function onAmountInput(e){
  const digits = String(e.target.value || '').replace(/\D/g, '')
  const num = Number(digits || '0') / 100
  withdrawAmountValue.value = num
  try {
    withdrawAmountDisplay.value = num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  } catch {
    withdrawAmountDisplay.value = `R$ ${num.toFixed(2)}`
  }
}
const canWithdraw = computed(() => {
  const val = withdrawAmountValue.value || 0
  return selectedBank.value && balanceAvailable.value > 0 && val > 0 && val <= balanceAvailable.value
})

function pad(n){ return String(n).padStart(2,'0') }
function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()}`
}
function formatNumber(v){
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
}
function formatCurrencyBRL(n){
  try { return Number(n||0).toLocaleString('pt-BR', { style:'currency', currency:'BRL' }) } catch { return `R$ ${Number(n||0).toFixed(2)}` }
}

async function fetchData() {
  loading.value = true
  try {
    // Sem endpoint de fechamentos por enquanto — mantemos grid vazio
    rows.value = []
  } finally {
    loading.value = false
  }
}
async function loadBankAccounts(){
  try {
    const { data } = await api.get('/api/finance/bank-accounts/')
    bankAccounts.value = data || []
  } catch { bankAccounts.value = [] }
  try {
    const { data } = await api.get('/api/finance/withdraw-requests/?status=pending')
    hasPendingWithdraw.value = Array.isArray(data) && data.length > 0
  } catch { hasPendingWithdraw.value = false }
  try {
    const { data } = await api.get('/api/finance/virtual-account/balance/')
    balanceAvailable.value = Number(data?.balance_available || 0)
  } catch { balanceAvailable.value = 0 }
}

function openWithdraw(){
  if (hasPendingWithdraw.value){
    alert('Você já possui uma solicitação de saque em aberto. Aguarde o processamento.')
    return
  }
  loadBankAccounts()
  showWithdraw.value = true
}

async function submitWithdraw(){
  if (submitting.value) return
  submitting.value = true
  try {
    if (!selectedBank.value) { alert('Selecione a conta de saque.'); submitting.value = false; return }
    if ((balanceAvailable.value || 0) <= 0) { alert('Saldo insuficiente para solicitar saque.'); submitting.value = false; return }
    const amount = withdrawAmountValue.value || 0
    if (amount <= 0) { alert('Informe um valor válido para saque.'); submitting.value = false; return }
    if (amount > balanceAvailable.value) { alert('Valor do saque não pode ultrapassar o saldo disponível.'); submitting.value = false; return }
    await api.post('/api/finance/withdraw-requests/', { bank_account: selectedBank.value, amount })
    alert(`Solicitação de saque enviada com sucesso no valor de ${formatCurrencyBRL(amount)}.\nVocê receberá conforme as regras de pagamento.`)
    showWithdraw.value = false
    await fetchData()
  } catch (e) {
    alert(`Não foi possível solicitar o saque.\nMotivo: ${extractErrorMessage(e)}`)
  } finally {
    submitting.value = false
  }
}

// helpers para exibir dados da conta selecionada
function displaySelected(part){
  const b = bankAccounts.value.find(x => x.id === selectedBank.value)
  if (!b) return ''
  if (part==='bank') return `${b.bank_code} - ${b.bank_name || ''}`
  if (part==='type') return b.account_type
  if (part==='agency') return `${b.agency_number}-${b.agency_digit || ''}`
  if (part==='account') return `${b.account_number}-${b.account_digit || ''}`
  return ''
}

function extractErrorMessage(err){
  try {
    const data = err?.response?.data
    if (!data) return err?.message || 'Erro desconhecido.'
    if (typeof data === 'string') return data
    if (Array.isArray(data)) return data.join(', ')
    // objeto de campos -> mensagens
    const parts = []
    for (const k of Object.keys(data)) {
      const v = Array.isArray(data[k]) ? data[k].join(', ') : String(data[k])
      parts.push(`${k}: ${v}`)
    }
    return parts.join(' | ') || 'Erro ao processar solicitação.'
  } catch {
    return 'Erro ao processar solicitação.'
  }
}

onMounted(fetchData)

const columns = [
  { key: 'id', label: 'ID', width: 'w-[80px]' },
  { key: 'closure_name', label: 'Fechamento' },
  { key: 'period_label', label: 'Período Ref.' },
  { key: 'amount_paid', label: 'Pagos', align: 'right' },
  { key: 'amount_unpaid', label: 'Não Pagos', align: 'right' },
  { key: 'details', label: 'Detalhes' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => (
    !q || [r.id, r.closure_name, r.period_label, r.details]
      .some(v => String(v || '').toLowerCase().includes(q))
  ))
})

function clearSearch() { search.value = '' }
function applySearch() {}

// Exportações
function exportExcel() {
  const header = ['ID','Fechamento','Período Ref.','Pagos','Não Pagos','Detalhes']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.closure_name}</td>`+
    `<td>${r.period_label}</td>`+
    `<td style="text-align:right;">${formatNumber(r.amount_paid)}</td>`+
    `<td style="text-align:right;">${formatNumber(r.amount_unpaid)}</td>`+
    `<td>${r.details}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_fechamentos_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.closure_name}</td>`+
    `<td>${r.period_label}</td>`+
    `<td style="text-align:right;">${formatNumber(r.amount_paid)}</td>`+
    `<td style="text-align:right;">${formatNumber(r.amount_unpaid)}</td>`+
    `<td>${r.details}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Relatório de Fechamentos</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
      td:nth-child(4),td:nth-child(5){text-align:right}
    </style>
  </head><body onload="window.print()">
    <h3>Relatório de Fechamentos</h3>
    <table>
      <thead><tr><th>ID</th><th>Fechamento</th><th>Período Ref.</th><th>Pagos</th><th>Não Pagos</th><th>Detalhes</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

// Altura mínima responsiva
const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}
onMounted(() => {
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))
</script>


