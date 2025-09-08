<template>
  <div class="space-y-3">
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <FileDown class="w-4 h-4" />
          <span>Exportar</span>
        </button>
        <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <Printer class="w-4 h-4" />
          <span>Imprimir</span>
        </button>
        <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
          <input v-model.trim="q" type="text" placeholder="Pesquisar por usuário..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
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
        <template #title>Solicitações de Saque</template>
        <template #actions="{ row }">
          <button class="inline-flex items-center justify-center w-8 h-8 rounded border border-gray-300 bg-gray-100 text-gray-600" title="Ação">
            <!-- Ícone fake até definir ação -->
            <MoreHorizontal class="w-4 h-4" />
          </button>
        </template>
        <template #col:created_at="{ row }">{{ formatDate(row.created_at) }}</template>
        <template #col:nameLogin="{ row }">
          <div class="text-[12px] leading-tight">
            <div>{{ row.full_name || '-' }}</div>
            <div><b>Login:</b> {{ row.username || '-' }}</div>
          </div>
        </template>
        <template #col:payment="{ row }">{{ row.payment || '-' }}</template>
        <template #col:amount="{ row }"><div class="text-right">R$ {{ Number(row.amount||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div></template>
        <template #col:status="{ row }"><span :class="statusBadgeClass(row.status)">{{ statusLabel(row.status) }}</span></template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'
import { FileDown, Printer, Search, Eraser, MoreHorizontal } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)
const q = ref('')

const columns = [
  { key: 'id', label: 'Id' },
  { key: 'created_at', label: 'Data da Solicitação' },
  { key: 'nameLogin', label: 'Nome/Login' },
  { key: 'payment', label: 'Tipo de Pagamento' },
  { key: 'amount', label: 'Valor', align: 'right' },
  { key: 'status', label: 'Status' },
]

const filtered = computed(() => {
  const term = (q.value || '').toLowerCase()
  return (rows.value || []).filter(r => !term || String(r.username||'').toLowerCase().includes(term))
})

function pad(n){ return String(n).padStart(2,'0') }
function formatDate(iso){
  try { if(!iso) return '-'; const d=new Date(iso); if(isNaN(d.getTime())) return '-'; return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}` } catch { return '-' }
}

function statusLabel(v){ const map={ pending:'Pendente', approved:'Aprovado', rejected:'Rejeitado' }; return map[v]||'-' }
function statusBadgeClass(v){
  switch(v){
    case 'approved': return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200'
    case 'rejected': return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-rose-50 text-rose-700 border border-rose-200'
    default: return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-amber-50 text-amber-700 border border-amber-200'
  }
}

async function loadData(){
  loading.value = true
  try {
    // Mock/placeholder: buscar transações contendo 'Saque'
    const { data } = await api.get('/api/finance/transactions/', { params: { } })
    rows.value = (data || []).filter(t => String(t.product||'').toLowerCase().includes('saque')).map((t,i)=>({
      id: t.id || i+1,
      username: t.licensed_username || '-',
      full_name: '',
      payment: t.payment_method || 'Pix',
      amount: t.amount,
      created_at: t.dtt_record || t.reference_date,
      status: t.status || 'pending',
    }))
  } catch { rows.value = [] } finally { loading.value = false; updateGridHeight() }
}

function exportExcel(){ /* simples, similar às outras telas */ }
function printGrid(){ /* simples, similar às outras telas */ }
function clearSearch(){ q.value = '' }
function applySearch(){}

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight(){ if(!gridWrapper.value) return; const rect = gridWrapper.value.getBoundingClientRect(); const available = window.innerHeight - rect.top - 16; gridMinHeight.value = `${Math.max(available, 300)}px` }

onMounted(loadData)
</script>

<style scoped>
</style>


