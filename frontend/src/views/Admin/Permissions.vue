<template>
  <div class="p-4">
    <div class="mb-3 bg-white rounded p-3 flex items-center gap-2 flex-wrap">
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white">Exportar</button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white">Imprimir</button>
      <input v-model.trim="q" placeholder="Buscar (app/codename)" class="border rounded px-2 py-1 h-8 text-xs min-w-[16rem]" />
      <select v-model="appFilter" class="border rounded px-2 py-1 h-8 text-xs">
        <option value="">App (todos)</option>
        <option v-for="a in appList" :key="a" :value="a">{{ a }}</option>
      </select>
    </div>
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'

const rows = ref([])
const loading = ref(false)
const q = ref('')
const appFilter = ref('')

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'app', label: 'App' },
  { key: 'codename', label: 'Codename' },
  { key: 'name', label: 'Nome' },
]

async function fetchPerms() {
  loading.value = true
  try {
    const { data } = await api.get('/api/core/admin/permissions/')
    rows.value = (data || []).map(p => ({
      id: p.id,
      app: p.content_type?.app_label,
      codename: p.codename,
      name: p.name,
    }))
  } finally { loading.value = false }
}

onMounted(fetchPerms)

const appList = computed(() => Array.from(new Set(rows.value.map(r => r.app))).filter(Boolean).sort())
const filteredRows = computed(() => rows.value.filter(r => {
  const mQ = !q.value || [r.app, r.codename, r.name].some(v => (v||'').toLowerCase().includes(q.value.toLowerCase()))
  const mApp = !appFilter.value || r.app === appFilter.value
  return mQ && mApp
}))

function exportExcel() {
  const header = ['ID','App','Codename','Nome']
  const body = filteredRows.value.map(r => `<tr><td>${r.id}</td><td>${r.app}</td><td>${r.codename}</td><td>${r.name}</td></tr>`).join('')
  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1"><thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `permissoes_${new Date().toISOString().slice(0,10)}.xls`
  a.click(); URL.revokeObjectURL(url)
}
function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => `<tr><td>${r.id}</td><td>${r.app}</td><td>${r.codename}</td><td>${r.name}</td></tr>`).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" /><title>Permissões</title><style>body{font-family:Arial} table{width:100%;border-collapse:collapse} th,td{border:1px solid #ddd;padding:6px;font-size:12px} th{background:#1e40af;color:#fff}</style></head><body onload=\"window.print()\"><h3>Permissões</h3><table><thead><tr><th>ID</th><th>App</th><th>Codename</th><th>Nome</th></tr></thead><tbody>${rowsHtml}</tbody></table></body></html>`
  win.document.write(html); win.document.close()
}
</script>


