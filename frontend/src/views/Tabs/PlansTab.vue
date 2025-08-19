<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Gerenciar Planos</h2>
      <button @click="newPlan" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Novo Plano</button>
    </div>

    <div ref="gridWrapper">
      <DataTable :columns="columns" :rows="decoratedRows" :loading="loading" :min-height="gridMinHeight">
        <template #title>Planos</template>
        <template #col:actions="{ row }">
          <button
            @click="editPlan(row)"
            class="h-[27px] w-7 grid place-items-center bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm transition"
            title="Editar"
          >
            <Pencil class="w-3.5 h-3.5" :stroke-width="1.75" />
          </button>
        </template>
        <template #col:id="{ row }">{{ row.id }}</template>
        <template #col:name="{ row }">{{ row.name }}</template>
        <template #col:price="{ row }">R$ {{ row.price }}</template>
        <template #col:points="{ row }">{{ row.points }}</template>
        <template #col:last_update="{ row }">
          <div class="text-[11px] leading-tight text-gray-700">
            <div>{{ row.usr_update_username || '-' }}</div>
            <div>{{ formatDate(row.dtt_update) }}</div>
          </div>
        </template>
        <template #col:stt_record="{ row }">
          <span :class="row.stt_record
            ? 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300'
            : 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-100 text-rose-800 border border-rose-300'">
            {{ row.stt_record ? 'Ativo' : 'Inativo' }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Modal criar/editar -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded w-full max-w-xl overflow-y-auto max-h-[90vh]">
        <div class="p-3 border-b font-semibold bg-blue-800 text-white">{{ form.id ? 'Editar Plano' : 'Cadastrar Novo Plano' }}</div>
        <div class="p-4 grid grid-cols-1 gap-4">
          <div class="flex items-center justify-between gap-4">
            <div class="flex-1">
              <label class="block mb-1">Nome</label>
              <input v-model="form.name" class="w-full border rounded px-2 py-1" />
            </div>
            <div class="flex items-center gap-2 mt-6">
              <span class="text-sm font-semibold">Status:</span>
              <label class="inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="form.stt_record" class="sr-only peer">
                <div class="w-9 h-5 bg-gray-300 rounded-full peer peer-checked:bg-green-500 relative transition-colors">
                  <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transform peer-checked:translate-x-4 transition-transform"></div>
                </div>
              </label>
            </div>
          </div>

          <div>
            <label class="block mb-1">Imagem (400x400)</label>
            <input type="file" @change="handleImageUpload" class="w-full border rounded px-2 py-1" />
            <div v-if="previewImage" class="mt-2">
              <img :src="previewImage" alt="Preview" class="w-32 h-32 object-cover border rounded" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block mb-1">Preço</label>
              <input v-model="form.price" type="number" step="0.01" class="w-full border rounded px-2 py-1" />
            </div>
            <div>
              <label class="block mb-1">Pontos</label>
              <input v-model="form.points" type="number" class="w-full border rounded px-2 py-1" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div v-for="n in 5" :key="n">
              <label class="block mb-1">Bônus Nível {{ n }}</label>
              <input v-model="form[`bonus_level_${n}`]" type="number" step="0.01" class="w-full border rounded px-2 py-1" />
            </div>
          </div>
        </div>
        <div class="p-3 border-t flex justify-end gap-2">
          <button @click="showModal = false" class="px-3 py-1.5 rounded border">Fechar</button>
          <button @click="savePlan" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
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
const showModal = ref(false)
const form = ref({})
const previewImage = ref(null)
const selectedImageFile = ref(null)

const columns = [
  { key: 'actions', label: 'Ações' },
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Nome' },
  { key: 'price', label: 'Preço' },
  { key: 'points', label: 'Pontos' },
  { key: 'last_update', label: 'Última Edição' },
  { key: 'stt_record', label: 'Status' },
]

onMounted(fetchPlans)

function fetchPlans() {
  loading.value = true
  api.get('/api/plans/plans/').then(res => {
    rows.value = res.data
  }).finally(() => loading.value = false)
}

const decoratedRows = computed(() => rows.value)

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

function newPlan() {
  form.value = { stt_record: true }
  previewImage.value = null
  selectedImageFile.value = null
  showModal.value = true
}

function editPlan(plan) {
  form.value = { ...plan }
  previewImage.value = plan.image ? plan.image : null
  showModal.value = true
}

function handleImageUpload(event) {
  const file = event.target.files[0]
  if (file) {
    selectedImageFile.value = file
    previewImage.value = URL.createObjectURL(file)
  }
}

function savePlan() {
  const fd = new FormData()
  fd.append('name', form.value.name)
  fd.append('price', form.value.price)
  fd.append('points', form.value.points)
  fd.append('bonus_level_1', form.value.bonus_level_1)
  fd.append('bonus_level_2', form.value.bonus_level_2)
  fd.append('bonus_level_3', form.value.bonus_level_3)
  fd.append('bonus_level_4', form.value.bonus_level_4)
  fd.append('bonus_level_5', form.value.bonus_level_5)
  fd.append('stt_record', form.value.stt_record)

  if (selectedImageFile.value) {
    fd.append('image', selectedImageFile.value)
  }

  const config = {
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: `Bearer ${localStorage.getItem('accessToken')}`
    }
  }

  if (form.value.id) {
    api.patch(`/api/plans/plans/${form.value.id}/`, fd, config).then(() => {
      fetchPlans()
      showModal.value = false
    })
  } else {
    api.post('/api/plans/plans/', fd, config).then(() => {
      fetchPlans()
      showModal.value = false
    })
  }
}

function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
onMounted(() => {
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))
</script>
