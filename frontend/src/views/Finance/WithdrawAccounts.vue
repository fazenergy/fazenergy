<template>
  <!-- Toolbar padrão -->
  <div class="mb-3 bg-white rounded">
    <div class="flex items-center gap-2 flex-wrap">
      <!-- + Adicionar -->
      <button @click="openNew" class="h-8 px-2 py-1 text-xs rounded bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm inline-flex items-center gap-1.5">
        <Plus class="w-4 h-4" />
        Adicionar
      </button>
      <!-- Exportar / Imprimir -->
      <button @click="exportList" class="h-8 px-2 py-1 text-xs rounded bg-purple-600 text-white hover:bg-purple-700 shadow-sm inline-flex items-center gap-1.5">
        <FileDown class="w-4 h-4" />
        Exportar
      </button>
      <button @click="printList" class="h-8 px-2 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-700 shadow-sm inline-flex items-center gap-1.5">
        <Printer class="w-4 h-4" />
        Imprimir
      </button>

      <!-- Info Regras (antes do filtro, após Imprimir) -->
      <button @click="showRules=true" class="inline-flex items-center justify-center w-8 h-8 rounded text-blue-600 hover:text-blue-700 border border-blue-200 hover:border-blue-300 shadow-sm" title="Regras de Saque">
        <Info class="w-4 h-4" />
      </button>

      <!-- Busca -->
      <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
        <input v-model.trim="search" type="text" placeholder="Pesquisar..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
        <button @click="applySearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 hover:bg-blue-700 text-white" title="Pesquisar">
          <Search class="w-4 h-4" />
        </button>
        <button @click="clearSearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 text-gray-700" title="Limpar">
          <Eraser class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>

  <!-- Grid -->
  <div ref="wrap" class="bg-white rounded border">
    <DataTable :columns="columns" :rows="filteredRows" :show-actions="true" :min-height="gridMinHeight">
      <template #title>Contas para Saque</template>
      <template #actions="{ row }">
        <div class="flex items-center gap-1.5">
          <button class="inline-flex items-center justify-center w-7 h-[27px] text-blue-600 hover:text-blue-700" title="Editar" @click="edit(row)">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4"><path d="M21.731 2.269a2.625 2.625 0 0 0-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 0 0 0-3.712ZM19.513 8.199l-3.712-3.712L3.91 16.378a5.25 5.25 0 0 0-1.32 2.214l-.8 2.685a.75.75 0 0 0 .928.928l2.685-.8a5.25 5.25 0 0 0 2.214-1.32L19.513 8.2Z"/></svg>
          </button>
        </div>
      </template>
      <template #col:is_default="{ row }">
        <span class="px-2 py-0.5 text-xs rounded" :class="row.is_default ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-700'">{{ row.is_default ? 'Sim' : 'Não' }}</span>
      </template>
    </DataTable>
  </div>

  <!-- Modal Cadastro/Edição -->
  <Modal v-model="showModal" :header-blue="true" :no-header-border="true">
    <template #title>{{ form.id ? 'Editar Conta' : 'Nova Conta' }}</template>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <!-- Tipo de titular -->
      <div>
        <label class="block text-xs text-gray-600 mb-1">Titular</label>
        <select v-model="form.owner_type" class="w-full border rounded px-2 py-1 h-8 text-sm">
          <option value="pf">Pessoa Física</option>
          <option value="pj">Pessoa Jurídica</option>
        </select>
      </div>
      <div v-if="form.owner_type==='pj'">
        <label class="block text-xs text-gray-600 mb-1">Empresa (CNPJ)</label>
        <select v-model="form.company" class="w-full border rounded px-2 py-1 h-8 text-sm">
          <option :value="null">Selecione</option>
          <option v-for="c in approvedCompanies" :key="c.id" :value="c.id">{{ c.cnpj }} — {{ c.razao_social }}</option>
        </select>
        <div v-if="!hasAnyCompany" class="mt-2 p-2 rounded border text-[12px] bg-blue-50 border-blue-200 text-blue-700">
          Para usar PJ, cadastre e valide sua empresa em "Minhas Empresas".
        </div>
      </div>

      <div>
        <label class="block text-xs text-gray-600 mb-1">Banco</label>
        <input v-model.trim="form.bank_code" placeholder="Código (ex.: 001)" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="block text-xs text-gray-600 mb-1">Nome do Banco</label>
        <input v-model.trim="form.bank_name" placeholder="Opcional" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>

      <div>
        <label class="block text-xs text-gray-600 mb-1">Tipo de Conta</label>
        <select v-model="form.account_type" class="w-full border rounded px-2 py-1 h-8 text-sm">
          <option value="corrente">Corrente</option>
          <option value="poupanca">Poupança</option>
          <option value="pagamento">Conta de Pagamento</option>
        </select>
      </div>

      <div>
        <label class="block text-xs text-gray-600 mb-1">Agência</label>
        <div class="flex gap-2">
          <input v-model.trim="form.agency_number" class="border rounded px-2 py-1 h-8 text-sm w-full" />
          <input v-model.trim="form.agency_digit" class="border rounded px-2 py-1 h-8 text-sm w-20" placeholder="Dígito" />
        </div>
      </div>
      <div>
        <label class="block text-xs text-gray-600 mb-1">Conta</label>
        <div class="flex gap-2">
          <input v-model.trim="form.account_number" class="border rounded px-2 py-1 h-8 text-sm w-full" />
          <input v-model.trim="form.account_digit" class="border rounded px-2 py-1 h-8 text-sm w-20" placeholder="Dígito" />
        </div>
      </div>

      <div>
        <label class="block text-xs text-gray-600 mb-1">{{ form.owner_type==='pj' ? 'Nome da Empresa' : 'Titular' }}</label>
        <input v-model.trim="form.account_holder_name" :readonly="form.owner_type==='pf'" :disabled="form.owner_type==='pf'" :class="['border rounded px-2 py-1 h-8 text-sm w-full', form.owner_type==='pf' ? 'bg-gray-100' : '']" />
      </div>
      <div>
        <label class="block text-xs text-gray-600 mb-1">{{ form.owner_type==='pj' ? 'CNPJ da Empresa' : 'CPF do Titular' }}</label>
        <input v-model.trim="form.account_holder_cpf_cnpj" :readonly="form.owner_type==='pf'" :disabled="form.owner_type==='pf'" :class="['border rounded px-2 py-1 h-8 text-sm w-full', form.owner_type==='pf' ? 'bg-gray-100' : '']" />
      </div>

      <div class="col-span-1 md:col-span-2 flex items-center gap-2">
        <input id="is_default" type="checkbox" v-model="form.is_default" class="h-4 w-4" />
        <label for="is_default" class="text-sm text-gray-700">Definir como conta padrão</label>
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2 py-2">
        <button class="px-4 py-2 rounded border" @click="showModal=false">Fechar</button>
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white" @click="save">Gravar</button>
      </div>
    </template>
  </Modal>

  <!-- Modal Regras -->
  <Modal v-model="showRules" :header-blue="true" :no-header-border="true">
    <template #title>Regras para Saque</template>
    <div class="space-y-2 text-sm text-gray-700">
      <div>Valor mínimo para saque: R$ {{ minWithdraw.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
      <div>Dias liberados para solicitar saque: {{ withdrawDays }}</div>
      <div>Solicitando hoje, previsão de pagamento: {{ payoutProjection }}</div>
      <div>Taxa por solicitação: R$ {{ feeFixed.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
      <div>Impostos devidos serão recolhidos na fonte e descontados no saque.</div>
      <div>Se houver uma solicitação em aberto, não é possível abrir outra até processamento.</div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import api from '@/services/axios'
import { Plus, FileDown, Printer, Search, Eraser, Info } from 'lucide-vue-next'
import { useAuthStore } from '@/store/auth'

const rows = ref([])
const search = ref('')
const showModal = ref(false)
const showRules = ref(false)
const auth = useAuthStore()
const form = ref({
  id: null,
  owner_type: 'pf',
  company: null,
  bank_code: '', bank_name: '', account_type: 'corrente',
  agency_number: '', agency_digit: '', account_number: '', account_digit: '',
  account_holder_name: '', account_holder_cpf_cnpj: '', is_default: true,
})

// Regras do sistema (poderia vir de endpoint de config)
const minWithdraw = ref(50)
const feeFixed = ref(10)
const withdrawDays = ref('Seg, Qua e Sex')
const payoutProjection = ref('próximo dia útil')

const approvedCompanies = ref([])
const hasAnyCompany = computed(() => Array.isArray(approvedCompanies.value) && approvedCompanies.value.length > 0)

const columns = [
  { key: 'id', label: 'ID', width: 'w-[80px]' },
  { key: 'owner_type', label: 'Titular' },
  { key: 'bank_code', label: 'Banco' },
  { key: 'account_type', label: 'Tipo' },
  { key: 'agency_full', label: 'Agência' },
  { key: 'account_full', label: 'Conta' },
  { key: 'is_default', label: 'Padrão', width: 'w-[100px]' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => !q || [r.bank_code, r.account_type, r.agency_full, r.account_full].some(v => String(v||'').toLowerCase().includes(q)))
})

function mapRow(r){
  return {
    ...r,
    owner_type: r.owner_type === 'pj' ? 'PJ' : 'PF',
    agency_full: `${r.agency_number || ''}-${r.agency_digit || ''}`,
    account_full: `${r.account_number || ''}-${r.account_digit || ''}`,
  }
}

async function fetchRows(){
  const { data } = await api.get('/api/finance/bank-accounts/')
  rows.value = (data || []).map(mapRow)
}

async function fetchCompanies(){
  try {
    const { data } = await api.get('/api/core/licensed-companies/?stt_validate=approved')
    approvedCompanies.value = data?.results || data || []
  } catch { approvedCompanies.value = [] }
}

function openNew(){
  form.value = { id:null, owner_type:'pf', company:null, bank_code:'', bank_name:'', account_type:'corrente', agency_number:'', agency_digit:'', account_number:'', account_digit:'', account_holder_name:'', account_holder_cpf_cnpj:'', is_default:true }
  showModal.value = true
}
function edit(row){
  form.value = { ...row, owner_type: row.owner_type === 'PJ' ? 'pj' : 'pf' }
  showModal.value = true
}
async function removeRow(row){
  if (!confirm('Excluir esta conta?')) return
  await api.delete(`/api/finance/bank-accounts/${row.id}/`)
  await fetchRows()
}
async function save(){
  const payload = { ...form.value }
  if (payload.owner_type !== 'pj') payload.company = null
  if (payload.id){
    await api.put(`/api/finance/bank-accounts/${payload.id}/`, payload)
  } else {
    await api.post('/api/finance/bank-accounts/', payload)
  }
  showModal.value = false
  await fetchRows()
}

function clearSearch(){ search.value = '' }
function applySearch(){}

// Altura responsiva do grid
const gridMinHeight = ref('300px')
const wrap = ref(null)
function updateH(){
  if (!wrap.value) return
  const rect = wrap.value.getBoundingClientRect()
  gridMinHeight.value = `${Math.max(window.innerHeight-rect.top-16, 300)}px`
}
onMounted(() => { fetchRows(); fetchCompanies(); updateH(); window.addEventListener('resize', updateH) })
onUnmounted(() => window.removeEventListener('resize', updateH))

// utilidades
function exportList(){}
function printList(){}

// ==========================
// Auto-preenchimento PF/PJ
// ==========================
function onlyDigits(v){
  try { return String(v || '').replace(/\D/g, '') } catch { return v }
}

const licensedFullName = computed(() => {
  const u = auth.user || {}
  const fn = (u.first_name || '').trim()
  const ln = (u.last_name || '').trim()
  const full = `${fn} ${ln}`.trim()
  return full || u.username || ''
})
const licensedCpf = computed(() => onlyDigits(auth.user?.cpf_cnpj))

watch(() => form.value.owner_type, (val) => {
  if (val === 'pf') {
    // PF: titular é o licenciado e campos bloqueados
    form.value.company = null
    form.value.account_holder_name = licensedFullName.value
    form.value.account_holder_cpf_cnpj = licensedCpf.value
  } else if (val === 'pj') {
    // PJ: usar dados da empresa quando selecionada; limpa por padrão
    form.value.account_holder_name = ''
    form.value.account_holder_cpf_cnpj = ''
  }
})

watch(() => form.value.company, (id) => {
  if (form.value.owner_type !== 'pj') return
  const comp = approvedCompanies.value.find(c => c.id === id)
  if (comp) {
    form.value.account_holder_name = comp.razao_social || ''
    form.value.account_holder_cpf_cnpj = onlyDigits(comp.cnpj)
  }
})
</script>


