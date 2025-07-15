<!-- src/views/Tabs/PlansTab.vue -->
<template>
  <div>
  <!-- Cabeçalho com botão alinhado à direita -->
   <div class="flex justify-between items-center mb-4">
    <h2 class="text-xl font-semibold">Gerenciar Planos</h2>

     <!-- Botão criar -->
      <button 
        @click="newPlan"
        class="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Novo Plano
      </button>
    </div>

    <!-- Tabela de planos -->
    <table class="w-full text-sm">
      <thead class="bg-gray-100">
        <tr>
          <th class="p-2 text-left">Nome</th>
          <th class="p-2 text-left">Preço</th>
          <th class="p-2 text-left">Pontos</th>
          <th class="p-2 text-left">Status</th>
          <th class="p-2 text-left">Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="plan in plans" :key="plan.id" class="border-b">
          <td class="p-2">{{ plan.name }}</td>
          <td class="p-2">R$ {{ plan.price }}</td>
          <td class="p-2">{{ plan.points }}</td>
          <td class="p-2">
            <span :class="plan.stt_record ? 'text-green-600' : 'text-red-600'">
              {{ plan.stt_record ? 'Ativo' : 'Inativo' }}
            </span>
          </td>
          <td class="p-2 space-x-2">
            <button @click="editPlan(plan)" class="text-blue-600">Editar</button>
            <button @click="deletePlan(plan.id)" class="text-red-600">Excluir</button>
          </td>
        </tr>
      </tbody>
    </table>

   

    <!-- Modal criar/editar -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded w-full max-w-xl overflow-y-auto max-h-[90vh]">
        <h3 class="text-lg font-semibold mb-4">
          {{ form.id ? 'Editar Plano' : 'Cadastrar Novo Plano' }}
        </h3>

        <div class="grid grid-cols-1 gap-4">
          <!-- Nome -->
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

          <!-- Upload imagem -->
          <div>
            <label class="block mb-1">Imagem (400x400)</label>
            <input
              type="file"
              @change="handleImageUpload"
              class="w-full border rounded px-2 py-1"
            />
            <div v-if="previewImage" class="mt-2">
              <img
                :src="previewImage"
                alt="Preview"
                class="w-32 h-32 object-cover border rounded"
              />
            </div>
          </div>

          <!-- Preço e Pontos -->
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block mb-1">Preço</label>
              <input
                v-model="form.price"
                type="number"
                step="0.01"
                class="w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label class="block mb-1">Pontos</label>
              <input
                v-model="form.points"
                type="number"
                class="w-full border rounded px-2 py-1"
              />
            </div>
          </div>

          <!-- Bônus níveis -->
          <div class="grid grid-cols-2 gap-2">
            <div v-for="n in 5" :key="n">
              <label class="block mb-1">Bônus Nível {{ n }}</label>
              <input
                v-model="form[`bonus_level_${n}`]"
                type="number"
                step="0.01"
                class="w-full border rounded px-2 py-1"
              />
            </div>
          </div>

        </div>

        <!-- Botões -->
        <div class="flex justify-end space-x-2 mt-6">
          <button
            @click="savePlan"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Salvar
          </button>
          <button
            @click="showModal = false"
            class="px-4 py-2 border rounded hover:bg-gray-100"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/axios'

const plans = ref([])
const showModal = ref(false)
const form = ref({})
const previewImage = ref(null)
const selectedImageFile = ref(null)

onMounted(() => {
  fetchPlans()
})

function fetchPlans() {
  api.get('/api/plans/plans/').then(res => {
    plans.value = res.data
  })
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
      // 👇 ISSO É CRÍTICO! Inclua o token manualmente se sobrescrever headers:
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

function deletePlan(id) {
  if (confirm('Tem certeza que deseja excluir este plano?')) {
    api.delete(`/api/plans/plans/${id}/`).then(fetchPlans)
  }
}
</script>
