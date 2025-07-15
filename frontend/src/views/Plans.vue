<template>
  <div>
    <h1 class="text-xl mb-4">Configuração de Plano</h1>
    <form @submit.prevent="savePlan" class="space-y-4">
      <input v-model="plan.name" placeholder="Nome do Plano" />
      <input type="number" v-model="plan.price" placeholder="Preço" />
      <input type="number" v-model="plan.points" placeholder="Pontos" />
      <!-- Bônus níveis -->
      <input type="number" v-model="plan.bonus_level_1" placeholder="Bônus Nível 1" />
      <input type="number" v-model="plan.bonus_level_2" placeholder="Bônus Nível 2" />
      <input type="number" v-model="plan.bonus_level_3" placeholder="Bônus Nível 3" />
      <input type="number" v-model="plan.bonus_level_4" placeholder="Bônus Nível 4" />
      <input type="number" v-model="plan.bonus_level_5" placeholder="Bônus Nível 5" />

      <!-- Upload de imagem -->
      <input type="file" @change="onFileChange" />
      <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded">Salvar</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/axios'

const plan = ref({
  name: '',
  price: 0,
  points: 0,
  bonus_level_1: 0,
  bonus_level_2: 0,
  bonus_level_3: 0,
  bonus_level_4: 0,
  bonus_level_5: 0,
  stt_record: true
})

const imageFile = ref(null)

function onFileChange(e) {
  imageFile.value = e.target.files[0]
}

async function savePlan() {
  const formData = new FormData()
  Object.entries(plan.value).forEach(([key, value]) => {
    formData.append(key, value)
  })
  if (imageFile.value) {
    formData.append('image', imageFile.value)
  }

  await api.post('/api/plans/plans/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

  alert('Plano salvo!')
}
</script>
