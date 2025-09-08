<template>
  <!-- Toolbar: ações e filtros (padrão) -->
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

      <select v-model="statusFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Status (todos)</option>
        <option value="blocked">Bloqueado</option>
        <option value="released">Liberado</option>
        <option value="canceled">Cancelado</option>
      </select>
      <select v-model="operationFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Operação (todas)</option>
        <option value="credit">Crédito</option>
        <option value="debit">Débito</option>
      </select>

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
      <template #title>Relatório de Bônus</template>
      <template #col:status="{ row }">
        <span :class="statusBadgeClass(row.status)">{{ statusLabel(row.status) }}</span>
      </template>
      <template #col:date="{ row }">{{ formatDate(row.date) }}</template>
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
const statusFilter = ref('')
const operationFilter = ref('')

function pad(n){ return String(n).padStart(2,'0') }
function formatDate(iso) {
  try {
    if (!iso) return '-'
    const d = new Date(iso)
    if (isNaN(d.getTime())) return '-'
    return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  } catch { return '-' }
}

function statusLabel(v) {
  const map = { blocked: 'Bloqueado', released: 'Liberado', canceled: 'Cancelado' }
  return map[v] || '-'
}

function operationLabel(v) {
  const map = { credit: 'Crédito', debit: 'Débito' }
  return map[v] || '-'
}

function statusBadgeClass(v) {
  switch (v) {
    case 'released':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200'
    case 'canceled':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-rose-50 text-rose-700 border border-rose-200'
    case 'blocked':
    default:
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-amber-50 text-amber-700 border border-amber-200'
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/api/network/bonus-references/')
    rows.value = (res.data || []).map((r, i) => ({
      id: i + 1,
      origin: `${r.product_name || 'Produto'}: Id ${r.product}`,
      licensed: r.receiver_username || '',
      amount: r.amount,
      date: r.created_at,
      status: r.status,
      _raw: r,
    }))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const columns = [
  { key: 'id', label: 'Id' },
  { key: 'origin', label: 'Produto/Origem' },
  { key: 'licensed', label: 'Licenciado' },
  { key: 'amount', label: 'Valor', align: 'right' },
  { key: 'date', label: 'Data' },
  { key: 'status', label: 'Status' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [
      String(r.id),
      String(r.licensed),
      String(r.product),
      String(r.description),
    ].some(v => (v || '').toString().toLowerCase().includes(q))
    const matchStatus = !statusFilter.value || r.status === statusFilter.value
    const matchOp = !operationFilter.value || r.operation === operationFilter.value
    return matchSearch && matchStatus && matchOp
  })
})

function clearSearch() { search.value = '' }
function applySearch() {}

// Exportações
function exportExcel() {
  const header = ['Id','Produto/Origem','Licenciado','Valor','Data','Status']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.origin}</td>`+
    `<td>${r.licensed}</td>`+
    `<td style=\"text-align:right;\">${r.amount}</td>`+
    `<td>${formatDate(r.date)}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset=\"utf-8\" /></head><body><table border=\"1\">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_bonus_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.origin}</td>`+
    `<td>${r.licensed}</td>`+
    `<td style=\"text-align:right;\">${r.amount}</td>`+
    `<td>${formatDate(r.date)}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset=\"utf-8\" />
    <title>Relatório de Bônus</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
      td:nth-child(7){text-align:right}
    </style>
  </head><body onload=\"window.print()\">
    <h3>Relatório de Bônus</h3>
    <table>
      <thead><tr><th>Id</th><th>Produto/Origem</th><th>Licenciado</th><th>Valor</th><th>Data</th><th>Status</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

// Altura mínima para colar rodapé
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


