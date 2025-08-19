<template>
  <div>
    <div class="mb-3 p-3 flex items-center justify-between">
      <button @click="newTemplate" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Novo Template</button>
      <div class="flex items-center gap-2">
        <input v-model.trim="search" placeholder="Pesquisar..." class="border rounded px-2 py-1 h-8 text-xs" />
        <button @click="clearSearch" class="px-2 py-1 h-8 text-xs border rounded hover:bg-gray-50">Limpar</button>
      </div>
    </div>

    <div ref="gridWrapper">
      <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
        <template #title>Templates de Contrato</template>
        <template #col:actions="{ row }">
          <button @click="editTemplate(row)" class="h-[27px] w-7 grid place-items-center bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm transition" title="Editar">
            <Pencil class="w-3.5 h-3.5" :stroke-width="1.75" />
          </button>
        </template>
        <template #col:id="{ row }">{{ row.id }}</template>
        <template #col:name="{ row }">{{ row.name }}</template>
        <template #col:active="{ row }">
          <span :class="row.active ? 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300' : 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-100 text-rose-800 border border-rose-300'">{{ row.active ? 'Ativo' : 'Inativo' }}</span>
        </template>
      </DataTable>
    </div>

    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white w-full max-w-6xl rounded shadow-lg">
        <div class="p-3 border-b font-semibold bg-blue-800 text-white">{{ form.id ? 'Editar Template' : 'Novo Template' }}</div>
        <div class="p-4 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
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
            <div class="md:col-span-3">
              <label class="text-xs text-gray-500">Descrição</label>
              <input v-model.trim="form.description" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div class="md:col-span-2">
              <div class="flex items-center justify-between">
                <label class="text-xs text-gray-500">Corpo (HTML)</label>
                <button @click="showGuide = !showGuide" class="text-xs underline">{{ showGuide ? 'Esconder guia' : 'Mostrar guia' }}</button>
              </div>
              <RichTextEditor v-model="form.body" minHeight="300px" maxHeight="300px" />
            </div>
            <div class="md:col-span-1" v-if="showGuide">
              <div class="border rounded p-3 bg-gray-50 h-[300px] md:h-[300px] overflow-auto">
                <div class="text-xs font-semibold mb-2">Guia de Chaves</div>
                <pre class="text-[11px] whitespace-pre-wrap">{{ mappingGuide }}</pre>
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
import RichTextEditor from '@/components/ui/RichTextEditor.vue'
import { Pencil } from 'lucide-vue-next'

const loading = ref(false)
const rows = ref([])
const search = ref('')

const columns = [
  { key: 'actions', label: 'Ações' },
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Nome' },
  { key: 'active', label: 'Status' },
]

async function fetchTemplates() {
  loading.value = true
  try {
    const { data } = await api.get('/api/contracts/templates/')
    rows.value = data
  } finally { loading.value = false }
}

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => !q || [r.name].some(v => (v || '').toLowerCase().includes(q)))
})

function clearSearch() { search.value = '' }
function newTemplate() { form.value = { active: true }; showModal.value = true }
function editTemplate(row) { form.value = { ...row }; showModal.value = true }

const showModal = ref(false)
const form = ref({ active: true })
const showGuide = ref(true)
const mappingGuide = computed(() => (form.value.mapping_info || defaultGuide).trim())

const defaultGuide = `{{ licensed.original_indicator }}: ID do Indicador Original
{{ licensed.id }}: ID do afiliado
{{ licensed.nome }}: Nome do licenciado
{{ licensed.person_type }}: Tipo de Pessoa PF ou PJ
{{ licensed.cpf_cnpj }}: CPF/CNPJ
{{ user.username }}: Nome de usuário
{{ user.email }}: E-mail do usuário
{{ site_url }}: URL do site
{{ licensed.phone }}: Telefone
{{ licensed.cep }}: CEP
{{ licensed.address }}: Endereço
{{ licensed.number }}: Número
{{ licensed.complement }}: Complemento
{{ licensed.district }}: Bairro
{{ licensed.city_name }}: Cidade
{{ licensed.state_abbr }}: UF
{{ licensed.plan.name }}: Nome do Plano
{{ licensed.plan.price }}: Preço do Plano
{{ licensed.full_name }}: Nome completo
{{ licensed.dtt_record }}: Data de cadastro
{{ licensed.dtt_payment_received }}: Data de pagamento`

async function saveTemplate() {
  const { mapping_info, ...payload } = form.value // não envia mapping_info (somente guia)
  if (payload.id) {
    await api.put(`/api/contracts/templates/${payload.id}/`, payload)
  } else {
    await api.post('/api/contracts/templates/', payload)
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
onMounted(() => { fetchTemplates(); updateGridHeight(); window.addEventListener('resize', updateGridHeight) })
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))
</script>


