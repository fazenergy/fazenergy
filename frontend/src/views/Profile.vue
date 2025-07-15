<template>
  <div class="flex">
    <div class="flex-1">
     <div class="p-6">
        <h1 class="text-2xl mb-4">Meu Perfil</h1>

        <div class="mb-4">
          <label class="block mb-1">Foto de Perfil Atual:</label>
          <img
            v-if="user.image_profile"
            :src="`${user.image_profile}`"
            alt="Profile"
            />
          <p v-else>Nenhuma foto enviada ainda.</p>
        </div>

        <div class="mb-4">
          <input type="file" @change="handleFileChange" />
        </div>

        <button
          @click="uploadImage"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          Salvar Foto
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import api from '@/services/axios'

const user = ref({})
const selectedFile = ref(null)

onMounted(async () => {
  const res = await api.get('/api/core/profile/')
  user.value = res.data
})

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const uploadImage = async () => {
  const formData = new FormData()
  formData.append('image_profile', selectedFile.value)

  await api.patch('/api/core/profile/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  alert('Foto atualizada com sucesso!')
  window.location.reload()
}
</script>

