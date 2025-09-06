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
        <option value="valid">Válido</option>
        <option value="pending">Pendente</option>
        <option value="canceled">Cancelado</option>
      </select>

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

  <div ref="gridWrapper">
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight" :show-actions="false">
      <template #title>Relatório de Pontos</template>
      <template #col:created_at="{ row }">{{ formatDate(row.created_at) }}</template>
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

function pad(n){ return String(n).padStart(2,'0') }
function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  const day = pad(d.getDate())
  const mon = pad(d.getMonth()+1)
  const yr = d.getFullYear()
  const hh = pad(d.getHours())
  const mm = pad(d.getMinutes())
  const ss = pad(d.getSeconds())
  return `${day}/${mon}/${yr} ${hh}:${mm}:${ss}`
}

function statusLabel(v) {
  const map = { valid: 'Válido', pending: 'Pendente', canceled: 'Cancelado' }
  return map[v] || '-'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/api/network/score-references/')
    rows.value = (res.data || []).map((r, i) => ({
      point_id: i + 1,
      created_at: r.created_at,
      sale_number: r.object_id,
      receiver_username: r.receiver_username,
      origin: r.origin_label || `${r.content_type_app || ''}.${r.content_type_model || ''}`,
      points_amount: r.points_amount,
      status: r.status,
      _uuid: r.id,
    }))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const columns = [
  { key: 'point_id', label: 'Id do Ponto' },
  { key: 'origin', label: 'Origem' },
  { key: 'sale_number', label: 'Nº Venda' },
  { key: 'receiver_username', label: 'Bonificado' },
  { key: 'points_amount', label: 'Qtd de Pontos', align: 'right' },
  { key: 'created_at', label: 'Lançamento' },
  { key: 'status', label: 'Status' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [r.point_id, r.sale_number, r.receiver_username, r.origin]
      .map(v => String(v || ''))
      .some(v => v.toLowerCase().includes(q))
    const matchStatus = !statusFilter.value || r.status === statusFilter.value
    return matchSearch && matchStatus
  })
})

function clearSearch() { search.value = '' }
function applySearch() {}

// Exportações
function exportExcel() {
  const header = ['Id do Ponto','Origem','Nº Venda','Bonificado','Qtd de Pontos','Lançamento','Status']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.point_id}</td>`+
    `<td>${r.origin}</td>`+
    `<td>${r.sale_number}</td>`+
    `<td>${r.receiver_username}</td>`+
    `<td style="text-align:right;">${r.points_amount}</td>`+
    `<td>${formatDate(r.created_at)}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `relatorio_pontos_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.point_id}</td>`+
    `<td>${r.origin}</td>`+
    `<td>${r.sale_number}</td>`+
    `<td>${r.receiver_username}</td>`+
    `<td style=\"text-align:right;\">${r.points_amount}</td>`+
    `<td>${formatDate(r.created_at)}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Relatório de Pontos</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Relatório de Pontos</h3>
    <table>
      <thead><tr><th>Id do Ponto</th><th>Origem</th><th>Nº Venda</th><th>Bonificado</th><th>Qtd de Pontos</th><th>Lançamento</th><th>Status</th></tr></thead>
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


