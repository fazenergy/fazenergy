<template>
  <!-- Toolbar padrão de relatórios -->
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
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'
import { FileDown, Printer, Search, Eraser } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)

const search = ref('')

function pad(n){ return String(n).padStart(2,'0') }
function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()}`
}
function formatNumber(v){
  return Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })
}

async function fetchData() {
  loading.value = true
  try {
    // Endpoint placeholder: ajuste quando o backend estiver disponível
    // Estrutura esperada por linha: { id, closure_name, period_label, amount_paid, amount_unpaid, details }
    const res = await api.get('/api/reports/closures/').catch(()=>({ data: [] }))
    rows.value = (res.data || []).map((r, i) => ({
      id: r.id ?? (i+1),
      closure_name: r.closure_name || '-',
      period_label: r.period_label || '-',
      amount_paid: r.amount_paid || 0,
      amount_unpaid: r.amount_unpaid || 0,
      details: r.details || '-',
      _raw: r,
    }))
  } finally {
    loading.value = false
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


