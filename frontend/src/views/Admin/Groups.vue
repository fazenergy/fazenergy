<template>
  <div class="p-4">
    <div class="mb-3 bg-white rounded p-3 flex items-center gap-2 flex-wrap">
      <button @click="openNew" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white">+ Adicionar</button>
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white">Exportar</button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white">Imprimir</button>
      <input v-model.trim="q" placeholder="Buscar grupo" class="border rounded px-2 py-1 h-8 text-xs min-w-[16rem]" />
    </div>
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" />

    <Modal v-model="showModal" :header-blue="true" :no-header-border="true">
      <template #title>{{ form.id ? 'Editar Grupo' : 'Novo Grupo' }}</template>
      <div class="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <input v-model.trim="form.name" placeholder="Nome do Grupo *" class="border rounded px-2 py-1" />
        <select multiple v-model="form.permissions" class="border rounded px-2 py-1 min-h-28">
          <option v-for="p in permissions" :key="p.id" :value="p.id">{{ p.content_type.app_label }}.{{ p.codename }}</option>
        </select>
      </div>
      <template #footer>
        <div class="flex items-center justify-end gap-2 py-2">
          <button class="px-4 py-2 rounded border" @click="showModal=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white" @click="save">Gravar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import api from '@/services/axios'

const rows = ref([])
const loading = ref(false)
const q = ref('')
const showModal = ref(false)
const permissions = ref([])
const form = ref({ id: null, name: '', permissions: [] })

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Nome' },
  { key: 'perms', label: 'Permissões' },
]

async function fetchAll() {
  loading.value = true
  try {
    const [g, p] = await Promise.all([
      api.get('/api/core/admin/groups/'),
      api.get('/api/core/admin/permissions/')
    ])
    permissions.value = p.data || []
    rows.value = (g.data || []).map(x => ({ id: x.id, name: x.name, perms: (x.permissions || []).length, _raw: x }))
  } finally { loading.value = false }
}

onMounted(fetchAll)

const filteredRows = computed(() => rows.value.filter(r => !q.value || (r.name||'').toLowerCase().includes(q.value.toLowerCase())))

function openNew() { form.value = { id: null, name: '', permissions: [] }; showModal.value = true }

async function save() {
  if (!form.value.name) return
  if (form.value.id) await api.patch(`/api/core/admin/groups/${form.value.id}/`, form.value)
  else await api.post('/api/core/admin/groups/', form.value)
  showModal.value = false
  await fetchAll()
}

function exportExcel() {
  const header = ['ID','Nome','Permissões']
  const body = filteredRows.value.map(r => `<tr><td>${r.id}</td><td>${r.name}</td><td>${r.perms}</td></tr>`).join('')
  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1"><thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `grupos_${new Date().toISOString().slice(0,10)}.xls`
  a.click(); URL.revokeObjectURL(url)
}
function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => `<tr><td>${r.id}</td><td>${r.name}</td><td>${r.perms}</td></tr>`).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" /><title>Grupos</title><style>body{font-family:Arial} table{width:100%;border-collapse:collapse} th,td{border:1px solid #ddd;padding:6px;font-size:12px} th{background:#1e40af;color:#fff}</style></head><body onload=\"window.print()\"><h3>Grupos</h3><table><thead><tr><th>ID</th><th>Nome</th><th>Permissões</th></tr></thead><tbody>${rowsHtml}</tbody></table></body></html>`
  win.document.write(html); win.document.close()
}
</script>


