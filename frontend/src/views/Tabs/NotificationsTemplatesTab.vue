<template>
  <div>
    <!-- Toolbar Templates -->
    <div class="mb-3 p-3 flex items-center justify-between">
      <button @click="newTemplate" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Novo Template</button>
      <div class="flex items-center gap-2">
        <input v-model.trim="search" placeholder="Pesquisar..." class="border rounded px-2 py-1 h-8 text-xs" />
        <button @click="clearSearch" class="px-2 py-1 h-8 text-xs border rounded hover:bg-gray-50">Limpar</button>
      </div>
    </div>

    <!-- Grid Templates -->
    <div ref="gridWrapper">
      <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
        <template #title>Templates de Notificação</template>
        <template #col:actions="{ row }">
          <div class="flex items-center gap-1">
            <button @click="editTemplate(row)" class="h-[27px] w-7 grid place-items-center bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm transition" title="Editar">
              <Pencil class="w-3.5 h-3.5" :stroke-width="1.75" />
            </button>
            <button @click="testTemplate(row)" class="h-7 px-2 grid place-items-center bg-gray-50 hover:bg-gray-100 text-gray-700 border rounded-md" title="Envio de Teste">
              Envio de Teste
            </button>
          </div>
        </template>
        <template #col:id="{ row }">{{ row.id }}</template>
        <template #col:name="{ row }">{{ row.name }}</template>
        <template #col:subject="{ row }">{{ row.subject }}</template>
        <template #col:active="{ row }">
          <span :class="row.active
            ? 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300'
            : 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-100 text-rose-800 border border-rose-300'">
            {{ row.active ? 'Ativo' : 'Inativo' }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Modal Template -->
    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white w-full max-w-2xl rounded shadow-lg">
        <div class="p-3 border-b font-semibold bg-blue-800 text-white">{{ form.id ? 'Editar Template' : 'Novo Template' }}</div>
        <div class="p-4 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-500">Nome</label>
              <input v-model.trim="form.name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-xs text-gray-500">Ativo?</label>
              <select v-model="form.active" class="w-full border rounded px-2 py-1 h-8 text-sm">
                <option :value="true">Sim</option>
                <option :value="false">Não</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-500">Assunto</label>
              <input v-model.trim="form.subject" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-500">Corpo</label>
              <div class="flex items-center gap-2 mb-2">
                <label class="inline-flex items-center gap-1 text-xs">
                  <input type="radio" value="rich" v-model="editorMode" /> Texto (Word)
                </label>
                <label class="inline-flex items-center gap-1 text-xs">
                  <input type="radio" value="html" v-model="editorMode" /> HTML (code)
                </label>
              </div>
              <div v-if="editorMode === 'rich'">
                <RichTextEditor v-model="form.body" />
              </div>
              <div v-else>
                <CodeEditor v-model="form.body" />
              </div>
            </div>
          </div>
        </div>
        <div class="p-3 border-t flex justify-end gap-2">
          <button @click="showModal = false" class="px-3 py-1.5 rounded border">Fechar</button>
          <button @click="saveTemplate" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'
import { Pencil } from 'lucide-vue-next'
import RichTextEditor from '@/components/ui/RichTextEditor.vue'
import CodeEditor from '@/components/ui/CodeEditor.vue'

const loading = ref(false)
const search = ref('')
const rows = ref([])
const smtpConfig = ref(null)

const showModal = ref(false)
const form = ref({ active: true })
const editorMode = ref('rich')

const columns = [
  { key: 'actions', label: 'Ações' },
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Nome' },
  { key: 'subject', label: 'Assunto' },
  { key: 'active', label: 'Status' },
]

async function fetchSMTP() {
  try {
    const { data } = await api.get('/api/notifications/config/')
    smtpConfig.value = data
  } catch {}
}

async function fetchTemplates() {
  loading.value = true
  try {
    const { data } = await api.get('/api/notifications/templates/')
    rows.value = data
  } finally { loading.value = false }
}

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => !q || [r.name, r.subject].some(v => (v || '').toLowerCase().includes(q)))
})

function clearSearch() { search.value = '' }
function newTemplate() { form.value = { active: true }; showModal.value = true }
function editTemplate(row) { form.value = { ...row }; showModal.value = true }

async function testTemplate(row) {
  const to = smtpConfig.value?.test_recipient || smtpConfig.value?.smtp_user
  try {
    await api.post(`/api/notifications/templates/${row.id}/test/`, { to })
    alert(`Email de teste enviado para ${to}`)
  } catch (e) {
    alert('Falha ao enviar teste')
  }
}

async function saveTemplate() {
  const payload = { ...form.value }
  if (payload.id) {
    await api.put(`/api/notifications/templates/${payload.id}/`, payload)
  } else {
    await api.post('/api/notifications/templates/', payload)
  }
  showModal.value = false
  await fetchTemplates()
}

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}
onMounted(() => {
  fetchSMTP();
  fetchTemplates();
  updateGridHeight();
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))
</script>


