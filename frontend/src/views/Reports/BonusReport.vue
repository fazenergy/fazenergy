<template>
  <!-- Toolbar: ações e filtros -->
  <div class="mb-3 bg-white border rounded p-3 flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
    <div class="flex items-center gap-2 flex-wrap">
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm">Exportar XLS</button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm">Imprimir / PDF</button>

      <div class="w-px h-6 bg-gray-200 mx-2" />

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
    </div>

    <div class="flex items-center gap-2 flex-1">
      <input v-model.trim="search" type="text" placeholder="Pesquisar..."
             class="w-full md:w-80 border rounded px-2 py-1 h-8 text-xs" />
      <button @click="clearSearch" class="px-2 py-1 h-8 text-xs border rounded hover:bg-gray-50">Limpar</button>
    </div>
  </div>

  <div ref="gridWrapper">
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight" :show-actions="false">
      <template #title>Relatório de Bônus</template>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'

const rows = ref([])
const loading = ref(false)

const search = ref('')
const statusFilter = ref('')
const operationFilter = ref('')

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

function statusLabel(v) {
  const map = { blocked: 'Bloqueado', released: 'Liberado', canceled: 'Cancelado' }
  return map[v] || '-'
}

function operationLabel(v) {
  const map = { credit: 'Crédito', debit: 'Débito' }
  return map[v] || '-'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/api/finance/transactions/')
    rows.value = (res.data || []).map(r => ({
      id: r.id,
      licensed: r.virtual_account?.licensed,
      product: r.product,
      description: r.description,
      status: r.status,
      operation: r.operation,
      amount: r.amount,
      reference_date: r.reference_date,
      dtt_record: r.dtt_record,
    }))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'licensed', label: 'Licenciado' },
  { key: 'product', label: 'Produto' },
  { key: 'description', label: 'Descrição' },
  { key: 'status', label: 'Status' },
  { key: 'operation', label: 'Operação' },
  { key: 'amount', label: 'Valor', align: 'right' },
  { key: 'reference_date', label: 'Ref.' },
  { key: 'dtt_record', label: 'Criação' },
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

// Exportações
function exportExcel() {
  const header = ['ID', 'Licenciado', 'Produto', 'Descrição', 'Status', 'Operação', 'Valor', 'Ref.', 'Criação']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.licensed}</td>`+
    `<td>${r.product}</td>`+
    `<td>${r.description || ''}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `<td>${operationLabel(r.operation)}</td>`+
    `<td style=\"text-align:right;\">${r.amount}</td>`+
    `<td>${r.reference_date}</td>`+
    `<td>${formatDate(r.dtt_record)}</td>`+
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
    `<td>${r.licensed}</td>`+
    `<td>${r.product}</td>`+
    `<td>${r.description || ''}</td>`+
    `<td>${statusLabel(r.status)}</td>`+
    `<td>${operationLabel(r.operation)}</td>`+
    `<td style=\"text-align:right;\">${r.amount}</td>`+
    `<td>${r.reference_date}</td>`+
    `<td>${formatDate(r.dtt_record)}</td>`+
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
      <thead><tr><th>ID</th><th>Licenciado</th><th>Produto</th><th>Descrição</th><th>Status</th><th>Operação</th><th>Valor</th><th>Ref.</th><th>Criação</th></tr></thead>
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


