<template>
  <!-- Toolbar: ações e filtros (padrão) -->
  <div class="mb-3 bg-white rounded">
    <div class="flex items-center gap-2 flex-wrap">
      <!-- Botões -->
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <FileDown class="w-4 h-4" />
        <span>Exportar</span>
      </button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <Printer class="w-4 h-4" />
        <span>Imprimir</span>
      </button>

      <!-- Target (operador/superadmin) -->
      <template v-if="canTarget">
        <input v-model.trim="targetInput" placeholder="Target (username)" class="border rounded px-2 py-1 h-8 text-xs min-w-[12rem]" />
        <button @click="applyTarget" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm">Aplicar</button>
      </template>

      <!-- Filtros -->
      <select v-model="planFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Plano (todos)</option>
        <option v-for="p in planOptions" :key="p" :value="p">{{ p }}</option>
      </select>
      <select v-model="cityFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Cidade (todas)</option>
        <option v-for="c in cityOptions" :key="c" :value="c">{{ c }}</option>
      </select>

      <!-- Busca expansível -->
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
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
      <template #title>Rede Completa</template>
      <template #col:user="{ row }">{{ row.user?.username }}</template>
      <template #col:upline="{ row }">{{ row.upline?.username || '-' }}</template>
      <template #col:level="{ row }">{{ row.level }}</template>
      <template #col:cpf_cnpj="{ row }">{{ row.cpf_cnpj }}</template>
      <template #col:phone="{ row }">{{ row.phone || '-' }}</template>
      <template #col:city="{ row }">{{ row.city_lookup?.name || row.city_name || '-' }}</template>
      <template #col:plan="{ row }">{{ row.plan?.name || '-' }}</template>
      <template #col:created="{ row }">{{ formatDate(row.dtt_record) }}</template>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'
import { useAuthStore } from '@/store/auth'
import { FileDown, Printer, Search, Eraser } from 'lucide-vue-next'

const auth = useAuthStore()
const canTarget = computed(() => auth.isSuperadmin || auth.isOperador)

const rows = ref([])
const loading = ref(false)
const targetInput = ref('')
let currentTarget = ''
const search = ref('')
const planFilter = ref('')
const cityFilter = ref('')

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

async function fetchData() {
  loading.value = true
  try {
    const url = currentTarget ? `/api/core/downlines/?target=${encodeURIComponent(currentTarget)}` : '/api/core/downlines/'
    const { data } = await api.get(url)
    rows.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const columns = [
  { key: 'user', label: 'Usuário' },
  { key: 'upline', label: 'Upline' },
  { key: 'level', label: 'Nível' },
  { key: 'cpf_cnpj', label: 'CPF/CNPJ' },
  { key: 'phone', label: 'Telefone' },
  { key: 'city', label: 'Cidade' },
  { key: 'plan', label: 'Plano' },
  { key: 'created', label: 'Cadastro' },
]

// Opções dinâmicas de filtros e filtragem
const planOptions = computed(() => {
  const set = new Set(rows.value.map(r => r.plan?.name).filter(Boolean))
  return Array.from(set).sort()
})
const cityOptions = computed(() => {
  const set = new Set(rows.value.map(r => r.city_lookup?.name || r.city_name).filter(Boolean))
  return Array.from(set).sort()
})

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [
      r.user?.username,
      r.upline?.username,
      r.cpf_cnpj,
      r.phone,
      r.city_lookup?.name || r.city_name,
      r.plan?.name
    ].some(v => (v || '').toString().toLowerCase().includes(q))

    const matchPlan = !planFilter.value || (r.plan?.name === planFilter.value)
    const matchCity = !cityFilter.value || ((r.city_lookup?.name || r.city_name) === cityFilter.value)
    return matchSearch && matchPlan && matchCity
  })
})

function applySearch() {
  // filtragem reativa
}

function clearSearch() {
  search.value = ''
}

// Exportações
function exportExcel() {
  const header = ['Usuário', 'Upline', 'Nível', 'CPF/CNPJ', 'Telefone', 'Cidade', 'Plano', 'Cadastro']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.user?.username || '')}</td>`+
    `<td>${(r.upline?.username || '')}</td>`+
    `<td>${(r.level ?? '')}</td>`+
    `<td>${(r.cpf_cnpj || '')}</td>`+
    `<td>${(r.phone || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.plan?.name || '')}</td>`+
    `<td>${formatDate(r.dtt_record) || ''}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `downlines_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.user?.username || '')}</td>`+
    `<td>${(r.upline?.username || '')}</td>`+
    `<td>${(r.level ?? '')}</td>`+
    `<td>${(r.cpf_cnpj || '')}</td>`+
    `<td>${(r.phone || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.plan?.name || '')}</td>`+
    `<td>${formatDate(r.dtt_record) || ''}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Rede Completa</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Rede Completa</h3>
    <table>
      <thead><tr><th>Usuário</th><th>Upline</th><th>Nível</th><th>CPF/CNPJ</th><th>Telefone</th><th>Cidade</th><th>Plano</th><th>Cadastro</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

function applyTarget() {
  currentTarget = targetInput.value
  fetchData()
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


