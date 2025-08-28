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

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

function statusLabel(v) {
  const map = { valid: 'Válido', pending: 'Pendente', canceled: 'Cancelado' }
  return map[v] || '-'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/api/network/score-references/')
    rows.value = (res.data || []).map(r => ({
      id: r.id,
      points_amount: r.points_amount,
      status: r.status,
      receiver: r.receiver_licensed,
      triggering: r.triggering_licensed,
      origin: `${r.content_type?.app_label}.${r.content_type?.model}`,
      object_id: r.object_id,
      created_at: r.created_at,
    }))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'points_amount', label: 'Pontos', align: 'right' },
  { key: 'status', label: 'Status' },
  { key: 'receiver', label: 'Recebedor' },
  { key: 'triggering', label: 'Causador' },
  { key: 'origin', label: 'Origem' },
  { key: 'object_id', label: 'Obj ID' },
  { key: 'created_at', label: 'Criação' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [
      String(r.id),
      String(r.receiver),
      String(r.triggering),
      String(r.origin),
      String(r.object_id),
    ].some(v => (v || '').toString().toLowerCase().includes(q))
    const matchStatus = !statusFilter.value || r.status === statusFilter.value
    return matchSearch && matchStatus
  })
})

function clearSearch() { search.value = '' }
function applySearch() {}

// Exportações
function exportExcel() {
  const header = ['ID', 'Pontos', 'Status', 'Recebedor', 'Causador', 'Origem', 'Obj ID', 'Criação']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td style="text-align:right;">${r.points_amount}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `<td>${r.receiver}</td>`+
    `<td>${r.triggering}</td>`+
    `<td>${r.origin}</td>`+
    `<td>${r.object_id}</td>`+
    `<td>${formatDate(r.created_at)}</td>`+
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
    `<td>${r.id}</td>`+
    `<td style="text-align:right;">${r.points_amount}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `<td>${r.receiver}</td>`+
    `<td>${r.triggering}</td>`+
    `<td>${r.origin}</td>`+
    `<td>${r.object_id}</td>`+
    `<td>${formatDate(r.created_at)}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Relatório de Pontos</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
      td:nth-child(2){text-align:right}
    </style>
  </head><body onload="window.print()">
    <h3>Relatório de Pontos</h3>
    <table>
      <thead><tr><th>ID</th><th>Pontos</th><th>Status</th><th>Recebedor</th><th>Causador</th><th>Origem</th><th>Obj ID</th><th>Criação</th></tr></thead>
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


