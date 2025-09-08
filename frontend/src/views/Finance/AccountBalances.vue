<template>
  <div class="space-y-3">
    <!-- Toolbar: Novo, Exportar, Imprimir, Info, Busca -->
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="openNew" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <Plus class="w-4 h-4" />
          <span>Novo</span>
        </button>
        <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <FileDown class="w-4 h-4" />
          <span>Exportar</span>
        </button>
        <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <Printer class="w-4 h-4" />
          <span>Imprimir</span>
        </button>
        <button @click="showInfo=true" class="inline-flex items-center justify-center w-9 h-9 rounded text-blue-600 hover:text-blue-700" title="Informações">
          <Info class="w-5 h-5" />
        </button>

        <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
          <input v-model.trim="q" type="text" placeholder="Pesquisar por nome ou login..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
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
      <DataTable :columns="columns" :rows="filtered" :loading="loading" :min-height="gridMinHeight">
        <template #title>Saldo de Contas</template>
        <template #actions="{ row }">
          <button class="inline-flex items-center justify-center w-8 h-8 rounded border border-gray-300 bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-800" title="Detalhes" @click="openDetails(row)">
            <FileText class="w-4 h-4" />
          </button>
        </template>
        <template #col:nameLogin="{ row }">
          <div class="text-[12px] leading-tight">
            <div>{{ row.full_name || '-' }}</div>
            <div><b>Login:</b> {{ row.licensed_username || '-' }}</div>
          </div>
        </template>
        <template #col:operation="{ row }">{{ operationLabel(row.operation) }}</template>
        <template #col:amount="{ row }"><div class="text-right">R$ {{ Number(row.amount||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div></template>
        <template #col:date="{ row }">{{ formatDate(row.date) }}</template>
      </DataTable>
    </div>

    <!-- Modal Info -->
    <Modal v-model="showInfo" :header-blue="true" :no-header-border="true">
      <template #title>Sobre esta tela</template>
      <div class="w-[560px] max-w-[90vw] p-1 text-sm leading-6">
        Esta tela é destinada a transações administrativas de contas virtuais (créditos/débitos). Use o botão <b>Novo</b> para lançar manualmente um crédito ou débito em nome de um licenciado.
      </div>
    </Modal>

    <!-- Modal Detalhes -->
    <Modal v-model="showDetails" :header-blue="true" :no-header-border="true">
      <template #title>Detalhes do Lançamento</template>
      <div class="w-[560px] max-w-[90vw] text-sm">
        <div class="space-y-1">
          <div><b>Usuário:</b> {{ selected?.licensed_username }}</div>
          <div><b>Operação:</b> {{ operationLabel(selected?.operation) }}</div>
          <div><b>Valor:</b> R$ {{ Number(selected?.amount||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
          <div><b>Data:</b> {{ formatDate(selected?.date) }}</div>
          <div><b>Descrição:</b> {{ selected?.description || '-' }}</div>
        </div>
      </div>
    </Modal>

    <!-- Modal Novo Lançamento -->
    <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
      <template #title>Novo Lançamento</template>
      <div class="w-[560px] max-w-[95vw]">
        <div v-if="newMsg" class="mb-2 px-3 py-2 rounded bg-blue-50 text-blue-700 border border-blue-200 text-sm">{{ newMsg }}</div>
        <div class="grid grid-cols-1 md:grid-cols-6 gap-3 text-sm">
          <div class="md:col-span-6 relative">
            <label class="text-xs text-gray-600">Login do Usuário</label>
            <div class="mt-1 flex gap-2">
              <input v-model.trim="newForm.username" type="text" class="flex-1 border rounded px-2 py-1 h-9" placeholder="Digite o login" @input="onUsernameInput" />
              <button @click="loadSuggestions" class="px-2 h-9 rounded border">Pesquisar</button>
            </div>
            <div v-if="suggestions.length" class="absolute z-10 mt-1 w-full bg-white border rounded shadow">
              <div v-for="s in suggestions" :key="s.user?.username" class="px-2 py-1 hover:bg-gray-100 cursor-pointer" @click="selectSuggestion(s)">
                {{ s.user?.full_name || '-' }} <span class="text-gray-500">| {{ s.user?.username }}</span>
              </div>
            </div>
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Operação</label>
            <select v-model="newForm.operation" class="mt-1 border rounded px-2 py-1 h-9 w-full">
              <option value="credit">Crédito</option>
              <option value="debit">Débito</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Valor</label>
            <input v-model="newForm.amount" type="number" step="0.01" min="0" class="mt-1 border rounded px-2 py-1 h-9 w-full" />
          </div>
          <div class="md:col-span-6">
            <label class="text-xs text-gray-600">Descrição (opcional)</label>
            <textarea v-model="newForm.description" class="mt-1 border rounded px-2 py-2 w-full" rows="3" placeholder="Observações"></textarea>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 rounded border text-sm" @click="showNew=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm inline-flex items-center gap-2" @click="saveNew" :disabled="savingNew">
            <span v-if="savingNew" class="inline-block h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
            <span>{{ savingNew ? 'Gravando...' : 'Gravar' }}</span>
          </button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import api from '@/services/axios'
import { FileText, FileDown, Printer, Search, Eraser, Plus, Info } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)
const q = ref('')

const columns = [
  { key: 'nameLogin', label: 'Nome do Licenciado / Login' },
  { key: 'operation', label: 'Tipo Operação' },
  { key: 'amount', label: 'Valor', align: 'right' },
  { key: 'date', label: 'Data' },
]

const filtered = computed(() => {
  const term = (q.value || '').toLowerCase()
  return (rows.value || []).filter(r => !term || (r.licensed_username||'').toLowerCase().includes(term) || (r.full_name||'').toLowerCase().includes(term))
})

function pad(n){ return String(n).padStart(2,'0') }
function formatDate(iso){ try { if(!iso) return '-'; const d = new Date(iso); if(isNaN(d.getTime())) return '-'; return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}` } catch { return '-' } }
function operationLabel(v){ return v === 'debit' ? 'Débito' : 'Crédito' }

async function loadRows(){
  loading.value = true
  try {
    const [{ data: tx }, { data: lic }] = await Promise.all([
      api.get('/api/finance/transactions/'),
      api.get('/api/core/licensed/')
    ])
    const usersByUsername = {}
    ;(lic?.results || lic || []).forEach(l => {
      const name = `${l.user?.first_name||''} ${l.user?.last_name||''}`.trim()
      if (l.user?.username) usersByUsername[l.user.username] = name
    })
    rows.value = (tx || []).map(t => ({
      id: t.id,
      licensed_username: t.licensed_username,
      full_name: usersByUsername[t.licensed_username] || '',
      operation: t.operation,
      amount: t.amount,
      date: t.dtt_record || t.reference_date,
      description: t.description,
    }))
  } catch { rows.value = [] } finally { loading.value = false; updateGridHeight() }
}

// Toolbar helpers
function clearSearch(){ q.value = '' }
function applySearch(){}

// Details modal
const showDetails = ref(false)
const selected = ref(null)
function openDetails(row){ selected.value = row; showDetails.value = true }

// Info modal
const showInfo = ref(false)

// New modal and logic
const showNew = ref(false)
const savingNew = ref(false)
const newForm = ref({ username: '', operation: 'credit', amount: '', description: '' })
const newMsg = ref('')

function openNew(){ newForm.value = { username: '', operation: 'credit', amount: '', description: '' }; newMsg.value=''; showNew.value = true }

const suggestions = ref([])
async function loadSuggestions(){
  try {
    const { data } = await api.get('/api/core/licensed/')
    const list = data?.results || data || []
    const term = (newForm.value.username || '').toLowerCase()
    suggestions.value = list.filter(l => !term || (l.user?.username||'').toLowerCase().includes(term) || (`${l.user?.first_name||''} ${l.user?.last_name||''}`.toLowerCase().includes(term)))
  } catch { suggestions.value = [] }
}
function onUsernameInput(){ if((newForm.value.username||'').length >= 2) loadSuggestions(); else suggestions.value = [] }
function selectSuggestion(l){ newForm.value.username = l.user?.username || ''; suggestions.value = [] }

async function saveNew(){
  if (!newForm.value.username) { newMsg.value = 'Informe o login.'; return }
  if (!newForm.value.amount || Number(newForm.value.amount) <= 0) { newMsg.value = 'Informe um valor válido.'; return }
  savingNew.value = true
  try {
    await api.post('/api/finance/transactions/', {
      licensed_username: newForm.value.username,
      operation: newForm.value.operation,
      amount: newForm.value.amount,
      description: newForm.value.description || ''
    })
    showNew.value = false
    await loadRows()
  } catch (e) {
    newMsg.value = 'Não foi possível gravar. Verifique os campos.'
  } finally { savingNew.value = false }
}

// Layout sizing
const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight(){ if(!gridWrapper.value) return; const rect = gridWrapper.value.getBoundingClientRect(); const available = window.innerHeight - rect.top - 16; gridMinHeight.value = `${Math.max(available, 300)}px` }

onMounted(loadRows)
</script>

<style scoped>
</style>


