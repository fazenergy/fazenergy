<template>
  <!-- Barra superior: botões + filtros (breadcrumb local removido) -->
  <div class="mb-3 bg-white rounded">
    <div class="flex items-center gap-2 flex-wrap">
      <!-- Botões (compactos) -->
      <button @click="openNewModal" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <Plus class="w-4 h-4" />
        <span>Adicionar</span>
      </button>
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <FileDown class="w-4 h-4" />
        <span>Exportar</span>
      </button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <Printer class="w-4 h-4" />
        <span>Imprimir</span>
      </button>

      <!-- Filtros ao lado -->
      <select v-model="planFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Plano (todos)</option>
        <option v-for="p in planOptions" :key="p" :value="p">{{ p }}</option>
      </select>
      <select v-model="cityFilter" class="border rounded px-2 py-1 h-8 text-xs min-w-[10rem]">
        <option value="">Cidade (todas)</option>
        <option v-for="c in cityOptions" :key="c" :value="c">{{ c }}</option>
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
  <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
    <template #title>Diretos</template>
    <template #col:user="{ row }">{{ row.user?.username }}</template>
    <template #col:cpf_cnpj="{ row }">{{ row.cpf_cnpj }}</template>
    <template #col:phone="{ row }">{{ row.phone || '-' }}</template>
    <template #col:city="{ row }">{{ row.city_lookup?.name || row.city_name || '-' }}</template>
    <template #col:plan="{ row }">{{ row.plan?.name || '-' }}</template>
    <template #col:created="{ row }">{{ formatDate(row.dtt_record) }}</template>
  </DataTable>
  </div>

  <!-- Modal Novo Licenciado -->
  <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
    <template #title>Novo Licenciado</template>
    <FormPreRegister :in-modal="true" :key="formKey" @close="showNew=false" />
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button @click="showNew=false" class="px-4 py-2 rounded border">Fechar</button>
        <button form="preRegisterForm" type="submit" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">Gravar</button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import FormPreRegister from '@/components/FormPreRegister.vue'
import api from '@/services/axios'
import { Plus, FileDown, Printer, Search, Eraser } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)
// filtro por upline removido
const search = ref('')
const planFilter = ref('')
const cityFilter = ref('')

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

onMounted(async () => {
  try {
    loading.value = true
    const { data } = await api.get('/api/core/directs/')
    rows.value = data
  } finally {
    loading.value = false
  }
})

const columns = [
  { key: 'user', label: 'Usuário' },
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
const planNameToId = {}
const cityOptions = computed(() => {
  const set = new Set(rows.value.map(r => r.city_lookup?.name || r.city_name).filter(Boolean))
  return Array.from(set).sort()
})

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [
      r.user?.username,
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
  // filtragem já é reativa; manter função para UX consistente
}

function clearSearch() {
  search.value = ''
}

// Exportações
function exportExcel() {
  // Gera uma tabela HTML simples com os dados filtrados e baixa como .xls
  const header = ['Usuário', 'CPF/CNPJ', 'Telefone', 'Cidade', 'Plano', 'Cadastro']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.user?.username || '')}</td>`+
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
  a.download = `diretos_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.user?.username || '')}</td>`+
    `<td>${(r.cpf_cnpj || '')}</td>`+
    `<td>${(r.phone || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.plan?.name || '')}</td>`+
    `<td>${formatDate(r.dtt_record) || ''}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Diretos</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Diretos</h3>
    <table>
      <thead><tr><th>Usuário</th><th>CPF/CNPJ</th><th>Telefone</th><th>Cidade</th><th>Plano</th><th>Cadastro</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

const showNew = ref(false)
const formKey = ref(0)
function openNewModal() { 
  formKey.value += 1
  showNew.value = true
}

// filtro por upline removido

// Calcula altura mínima para o grid ocupar até o rodapé
const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16 // margem inferior
  gridMinHeight.value = `${Math.max(available, 300)}px`
}
onMounted(() => {
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))
</script>


