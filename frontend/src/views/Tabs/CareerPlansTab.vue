<template>
  <div>
    <!-- Toolbar -->
    <div class="mb-3 p-3 flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="newCareerPlan" class="px-3 py-1.5 h-9 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm">Novo Plano de Carreira</button>
      </div>
      <div class="flex items-center gap-2 flex-1">
        <input v-model.trim="search" type="text" placeholder="Pesquisar..." class="w-full md:w-80 border rounded px-2 py-1 h-8 text-xs" />
        <button @click="clearSearch" class="px-2 py-1 h-8 text-xs border rounded hover:bg-gray-50">Limpar</button>
      </div>
    </div>

    <!-- Grid -->
    <div ref="gridWrapper">
      <DataTable :columns="columns" :rows="decoratedRows" :loading="loading" :min-height="gridMinHeight">
        <template #title>Planos de Carreira</template>
        <template #col:id="{ row }">{{ row.id }}</template>
        <template #col:stage_name="{ row }">{{ row.stage_name }}</template>
        <template #col:reward_description="{ row }">{{ row.reward_description }}</template>
        <template #col:required_points="{ row }">{{ row.required_points }}</template>
        <template #col:required_directs="{ row }">{{ row.required_directs }}</template>
        <template #col:required_direct_sales="{ row }">{{ row.required_direct_sales }}</template>
        <template #col:max_pml_per_line="{ row }">{{ row.max_pml_per_line }}</template>
        <template #col:last_update="{ row }">
          <div class="text-[11px] leading-tight text-gray-700">
            <div>{{ row.usr_update_username || '-' }}</div>
            <div>{{ formatDate(row.dtt_update) }}</div>
          </div>
        </template>
        <template #col:actions="{ row }">
          <button
            @click="editCareerPlan(row)"
            class="h-[27px] w-7 grid place-items-center bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm transition"
            title="Editar"
          >
            <Pencil class="w-3.5 h-3.5" :stroke-width="1.75" />
          </button>
        </template>
        <template #col:stt_record="{ row }">
          <span
            :class="row.stt_record
              ? 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300'
              : 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-100 text-rose-800 border border-rose-300'">
            {{ row.stt_record ? 'Ativo' : 'Inativo' }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Modal Novo -->
    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white w-full max-w-lg rounded shadow-lg">
        <div class="p-3 border-b font-semibold bg-blue-800 text-white">{{ form.id ? 'Editar Plano de Carreira' : 'Novo Plano de Carreira' }}</div>
        <div class="p-4 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-500">Estágio</label>
              <input v-model.trim="form.stage_name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-xs text-gray-500">Pontos Necessários</label>
              <input v-model.number="form.required_points" type="number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-xs text-gray-500">Qtd de Diretos</label>
              <input v-model.number="form.required_directs" type="number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-xs text-gray-500">Vendas Diretas</label>
              <input v-model.number="form.required_direct_sales" type="number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-xs text-gray-500">PML Máx por Linha</label>
              <input v-model.number="form.max_pml_per_line" type="number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-xs text-gray-500">Ativo?</label>
              <select v-model="form.stt_record" class="w-full border rounded px-2 py-1 h-8 text-sm">
                <option :value="true">Sim</option>
                <option :value="false">Não</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-500">Prêmio</label>
              <input v-model.trim="form.reward_description" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-500">Imagem de Capa (opcional)</label>
              <input type="file" accept="image/*" @change="handleImageUpload" class="w-full text-sm" />
              <img v-if="previewImage" :src="previewImage" alt="preview" class="mt-2 h-24 object-cover rounded border" />
            </div>
          </div>
        </div>
        <div class="p-3 border-t flex justify-end gap-2">
          <button @click="showModal = false" class="px-3 py-1.5 rounded border">Fechar</button>
          <button @click="saveCareerPlan" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
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

const rows = ref([])
const loading = ref(false)
const search = ref('')

const showModal = ref(false)
const form = ref({ stt_record: true })
const selectedImageFile = ref(null)
const previewImage = ref(null)

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

async function fetchCareerPlans() {
  loading.value = true
  try {
    const { data } = await api.get('/api/plans/plan-careers/')
    rows.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchCareerPlans)

const columns = [
  { key: 'actions', label: 'Ações' },
  { key: 'id', label: 'ID' },
  { key: 'stage_name', label: 'Estágio' },
  { key: 'reward_description', label: 'Prêmio' },
  { key: 'required_points', label: 'Pontos' },
  { key: 'required_directs', label: 'Diretos' },
  { key: 'required_direct_sales', label: 'Vendas Diretas' },
  { key: 'max_pml_per_line', label: 'PML Máx/Linha' },
  { key: 'last_update', label: 'Última Edição' },
  { key: 'stt_record', label: 'Status' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => !q || [
    r.stage_name,
    r.reward_description,
    r.required_points,
    r.required_directs,
    r.required_direct_sales,
    r.max_pml_per_line
  ].some(v => (v ?? '').toString().toLowerCase().includes(q)))
})

const decoratedRows = computed(() => filteredRows.value)

function clearSearch() { search.value = '' }

function newCareerPlan() {
  form.value = { stt_record: true }
  selectedImageFile.value = null
  previewImage.value = null
  showModal.value = true
}

function editCareerPlan(row) {
  form.value = { ...row }
  previewImage.value = row.cover_image || null
  selectedImageFile.value = null
  showModal.value = true
}

function handleImageUpload(event) {
  const file = event.target.files[0]
  if (file) {
    selectedImageFile.value = file
    previewImage.value = URL.createObjectURL(file)
  } else {
    selectedImageFile.value = null
    previewImage.value = null
  }
}

async function saveCareerPlan() {
  const fd = new FormData()
  fd.append('stage_name', form.value.stage_name || '')
  fd.append('reward_description', form.value.reward_description || '')
  fd.append('required_points', form.value.required_points ?? 0)
  fd.append('required_directs', form.value.required_directs ?? 0)
  fd.append('required_direct_sales', form.value.required_direct_sales ?? 0)
  fd.append('max_pml_per_line', form.value.max_pml_per_line ?? 0)
  fd.append('stt_record', form.value.stt_record ? 'true' : 'false')
  if (selectedImageFile.value) fd.append('cover_image', selectedImageFile.value)

  if (form.value.id) {
    await api.patch(`/api/plans/plan-careers/${form.value.id}/`, fd)
  } else {
    await api.post('/api/plans/plan-careers/', fd)
  }
  showModal.value = false
  await fetchCareerPlans()
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


