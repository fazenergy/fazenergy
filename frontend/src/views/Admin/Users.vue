<template>
  <div class="flex">
    <div class="flex-1">
      <div class="p-4">
        <!-- Toolbar -->
        <div class="mb-3 bg-white rounded p-3 flex items-center gap-2 flex-wrap">
          <button @click="openNew" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white inline-flex items-center gap-1.5">
            <span>+ Adicionar</span>
          </button>
          <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white inline-flex items-center gap-1.5">
            Exportar
          </button>
          <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white inline-flex items-center gap-1.5">
            Imprimir
          </button>

          <input v-model.trim="q" placeholder="Buscar (username/nome/email)" class="border rounded px-2 py-1 h-8 text-xs min-w-[16rem]" />
          <select v-model="groupFilter" class="border rounded px-2 py-1 h-8 text-xs">
            <option value="">Grupo (todos)</option>
            <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
          <select v-model="statusFilter" class="border rounded px-2 py-1 h-8 text-xs">
            <option value="">Status (todos)</option>
            <option value="active">Ativos</option>
            <option value="inactive">Inativos</option>
          </select>
        </div>

        <!-- Grid -->
        <div ref="gridWrapper">
          <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight" />
        </div>
      </div>
    </div>

    <Modal v-model="showModal" :header-blue="true" :no-header-border="true">
      <template #title>{{ form.id ? 'Editar Usuário' : 'Novo Usuário' }}</template>
      <div class="mt-2 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Coluna esquerda: anexo de foto -->
        <div class="space-y-3">
          <div class="border rounded p-3 text-sm">
            <div class="font-semibold mb-2">Foto de Perfil</div>
            <input type="file" @change="onPickImage" />
          </div>
        </div>
        <!-- Coluna direita: abas -->
        <div class="lg:col-span-2 space-y-4">
          <div class="border rounded p-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <input v-model.trim="form.username" placeholder="Username *" class="border rounded px-2 py-1" />
              <input v-model.trim="form.email" type="email" placeholder="E-mail *" class="border rounded px-2 py-1" />
              <input v-model.trim="form.first_name" placeholder="Nome" class="border rounded px-2 py-1" />
              <input v-model.trim="form.last_name" placeholder="Sobrenome" class="border rounded px-2 py-1" />
              <label class="inline-flex items-center gap-2 text-sm mt-1"><input type="checkbox" v-model="form.is_active" /> Ativo</label>
              <label class="inline-flex items-center gap-2 text-sm mt-1"><input type="checkbox" v-model="form.is_staff" /> Staff</label>
            </div>
          </div>
          <div class="border rounded p-3">
            <div class="font-semibold mb-2">Senha</div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <input v-model.trim="pwd" type="password" placeholder="Senha" class="border rounded px-2 py-1" />
              <input v-model.trim="pwd2" type="password" placeholder="Confirmar Senha" class="border rounded px-2 py-1" />
            </div>
          </div>
          <div class="border rounded p-3">
            <div class="font-semibold mb-2">Grupos & Permissões</div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <select multiple v-model="form.groups" class="border rounded px-2 py-1 min-h-24">
                <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
              <select multiple v-model="form.user_permissions" class="border rounded px-2 py-1 min-h-24">
                <option v-for="p in permissions" :key="p.id" :value="p.id">{{ p.content_type.app_label }}.{{ p.codename }}</option>
              </select>
            </div>
          </div>
        </div>
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
import { ref, onMounted, computed, onUnmounted } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import api from '@/services/axios'

const rows = ref([])
const loading = ref(false)
const q = ref('')
const groupFilter = ref('')
const statusFilter = ref('')

const groups = ref([])
const permissions = ref([])

const showModal = ref(false)
const form = ref({ id: null, username: '', email: '', first_name: '', last_name: '', is_active: true, is_staff: false, groups: [], user_permissions: [] })
let imageFile = null
const pwd = ref('')
const pwd2 = ref('')

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'username', label: 'Username' },
  { key: 'name', label: 'Nome' },
  { key: 'email', label: 'E-mail' },
  { key: 'is_active', label: 'Ativo' },
  { key: 'updated', label: 'Atualização' },
]

async function fetchGroupsPerms() {
  const [g, p] = await Promise.all([
    api.get('/api/core/admin/groups/'),
    api.get('/api/core/admin/permissions/')
  ])
  groups.value = g.data || []
  permissions.value = p.data || []
}

async function fetchUsers() {
  loading.value = true
  try {
    const { data } = await api.get('/api/core/admin/users/')
    rows.value = (data || []).map(u => ({
      id: u.id,
      username: u.username,
      name: `${u.first_name || ''} ${u.last_name || ''}`.trim(),
      email: u.email,
      is_active: u.is_active ? 'Sim' : 'Não',
      updated: u.last_login || u.date_joined,
      _raw: u,
    }))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchGroupsPerms()
  await fetchUsers()
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))

const filteredRows = computed(() => {
  const query = (q.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchQ = !query || [r.username, r.name, r.email].some(v => (v||'').toLowerCase().includes(query))
    const matchGroup = !groupFilter.value || (r._raw.groups || []).includes(Number(groupFilter.value))
    const matchStatus = !statusFilter.value || (statusFilter.value === 'active' ? r._raw.is_active : !r._raw.is_active)
    return matchQ && matchGroup && matchStatus
  })
})

function openNew() {
  form.value = { id: null, username: '', email: '', first_name: '', last_name: '', is_active: true, is_staff: false, groups: [], user_permissions: [] }
  pwd.value = ''
  pwd2.value = ''
  imageFile = null
  showModal.value = true
}

function onPickImage(e) { imageFile = e.target.files?.[0] || null }

async function save() {
  if (!form.value.username || !form.value.email) {
    alert('Preencha Username e E-mail.')
    return
  }
  // Regras de senha: obrigatória na criação; opcional na edição
  if (!form.value.id) {
    if (!pwd.value) { alert('Senha é obrigatória para novo usuário.'); return }
    if (pwd.value !== pwd2.value) { alert('As senhas não conferem.'); return }
  } else {
    if ((pwd.value || pwd2.value) && pwd.value !== pwd2.value) { alert('As senhas não conferem.'); return }
  }
  const fd = new FormData()
  Object.entries(form.value).forEach(([k, v]) => {
    if (Array.isArray(v)) v.forEach(val => fd.append(k, val))
    else if (v !== null && v !== undefined) fd.append(k, v)
  })
  if (pwd.value) fd.append('password', pwd.value)
  if (imageFile) fd.append('image_profile', imageFile)
  if (form.value.id) await api.patch(`/api/core/admin/users/${form.value.id}/`, fd)
  else await api.post('/api/core/admin/users/', fd)
  showModal.value = false
  await fetchUsers()
}

// Helpers
const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

function exportExcel() {
  const header = ['ID','Username','Nome','E-mail','Ativo','Atualização']
  const body = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.username}</td>`+
    `<td>${r.name}</td>`+
    `<td>${r.email}</td>`+
    `<td>${r.is_active}</td>`+
    `<td>${formatDate(r.updated)}</td>`+
    `</tr>`
  )).join('')
  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${body}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `usuarios_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${r.id}</td>`+
    `<td>${r.username}</td>`+
    `<td>${r.name}</td>`+
    `<td>${r.email}</td>`+
    `<td>${r.is_active}</td>`+
    `<td>${formatDate(r.updated)}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Usuários</title>
    <style>
      body{font-family: Arial, sans-serif;} table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Usuários</h3>
    <table>
      <thead><tr><th>ID</th><th>Username</th><th>Nome</th><th>E-mail</th><th>Ativo</th><th>Atualização</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}
</script>


