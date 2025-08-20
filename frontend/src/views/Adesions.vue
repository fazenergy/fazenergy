<template>
  <!-- Toolbar: ações e filtros -->
  <div class="mb-3 bg-white border rounded p-3 flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
    <div class="flex items-center gap-2 flex-wrap">
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm">Exportar XLS</button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm">Imprimir / PDF</button>

      <div class="w-px h-6 bg-gray-200 mx-2" />

      <select v-model="planFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Plano (todos)</option>
        <option v-for="p in planOptions" :key="p" :value="p">{{ p }}</option>
      </select>
      <select v-model="paymentStatusFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Pagamento (todos)</option>
        <option v-for="s in paymentStatusOptions" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div class="flex items-center gap-2 flex-1">
      <input v-model.trim="search" type="text" placeholder="Pesquisar..."
             class="w-full md:w-80 border rounded px-2 py-1 h-8 text-xs" />
      <button @click="clearSearch" class="px-2 py-1 h-8 text-xs border rounded hover:bg-gray-50">Limpar</button>
    </div>
  </div>

  <div ref="gridWrapper">
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
      <template #title>Adesões</template>

      <template #col:id="{ row }">#{{ row.id }}</template>
      <template #col:plan="{ row }">{{ planName(row.plan) }}</template>
      <template #col:licensed="{ row }">{{ licensedLabel(row) }}</template>
      <template #col:payment_type="{ row }">{{ paymentTypeLabel(row.typ_payment) }}</template>
      <template #col:created="{ row }">{{ formatDate(row.dtt_record) }}</template>
      <template #col:paid_at="{ row }">{{ formatDate(row.dtt_payment) }}</template>
      <template #col:payment_status="{ row }">
        <span :class="paymentStatusBadgeClass(row.ind_payment_status)">
          {{ paymentStatusLabel(row.ind_payment_status) }}
        </span>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'

const rows = ref([])
const loading = ref(false)
const plansMap = ref({})

const search = ref('')
const planFilter = ref('')
const paymentStatusFilter = ref('')

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

function paymentStatusLabel(v) {
  const map = { pending: 'Pendente', confirmed: 'Confirmado', canceled: 'Cancelado' }
  return map[v] || '-'
}

function paymentStatusBadgeClass(v) {
  switch (v) {
    case 'pending':
      return 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-100 text-amber-800 border border-amber-300'
    case 'confirmed':
      return 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300'
    case 'canceled':
      return 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-100 text-rose-800 border border-rose-300'
    default:
      return 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-700 border border-gray-300'
  }
}

function paymentTypeLabel(v) {
  const map = { pix: 'Pix', money: 'Dinheiro', creditCard: 'Cartão de Crédito', debitCard: 'Cartão de Débito' }
  return map[v] || '-'
}

function planName(id) {
  return plansMap.value[id] || `#${id}`
}

function licensedLabel(row) {
  const uname = row.licensed_username
  if (uname) return `${row.licensed}-${uname}`
  return String(row.licensed ?? '-')
}

async function fetchData() {
  loading.value = true
  try {
    const [adesionsRes, plansRes] = await Promise.all([
      api.get('/api/plans/plan-adesions/'),
      api.get('/api/plans/plans/')
    ])
    rows.value = adesionsRes.data
    plansMap.value = Object.fromEntries((plansRes.data || []).map(p => [p.id, p.name]))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'plan', label: 'Plano' },
  { key: 'licensed', label: 'Licenciado' },
  { key: 'payment_type', label: 'Tipo' },
  { key: 'created', label: 'Criação' },
  { key: 'paid_at', label: 'Pagamento' },
  { key: 'payment_status', label: 'Status Pag.' }
]

const planOptions = computed(() => {
  return Object.values(plansMap.value).sort()
})

const paymentStatusOptions = ['Pendente', 'Confirmado', 'Cancelado']

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const planStr = planName(r.plan)
    const sttStr = paymentStatusLabel(r.ind_payment_status)
    const typeStr = paymentTypeLabel(r.typ_payment)
    const licStr = licensedLabel(r)
    const matchSearch = !q || [
      String(r.id),
      licStr,
      planStr,
      sttStr,
      typeStr
    ].some(v => (v || '').toString().toLowerCase().includes(q))

    const matchPlan = !planFilter.value || (planStr === planFilter.value)
    const matchStatus = !paymentStatusFilter.value || (sttStr === paymentStatusFilter.value)
    return matchSearch && matchPlan && matchStatus
  })
})

function clearSearch() {
  search.value = ''
}

// Exportações
function exportExcel() {
  const header = ['ID', 'Plano', 'Licenciado', 'Tipo', 'Criação', 'Pagamento', 'Status Pag.']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${planName(r.plan)}</td>`+
    `<td>${licensedLabel(r)}</td>`+
    `<td>${paymentTypeLabel(r.typ_payment)}</td>`+
    `<td>${formatDate(r.dtt_record)}</td>`+
    `<td>${formatDate(r.dtt_payment)}</td>`+
    `<td>${paymentStatusLabel(r.ind_payment_status)}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `adesoes_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${planName(r.plan)}</td>`+
    `<td>${licensedLabel(r)}</td>`+
    `<td>${paymentTypeLabel(r.typ_payment)}</td>`+
    `<td>${formatDate(r.dtt_record)}</td>`+
    `<td>${formatDate(r.dtt_payment)}</td>`+
    `<td>${paymentStatusLabel(r.ind_payment_status)}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Adesões</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Adesões</h3>
    <table>
      <thead><tr><th>ID</th><th>Plano</th><th>Licenciado</th><th>Tipo</th><th>Criação</th><th>Pagamento</th><th>Status Pag.</th></tr></thead>
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

