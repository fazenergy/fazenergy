<template>
  <div class="bg-white rounded border overflow-hidden">
    <!-- Header azul -->
    <div class="px-4 py-3 bg-blue-600 text-white font-semibold">Meu Perfil</div>

    <!-- Corpo -->
    <div class="p-4">
      <form @submit.prevent="saveProfile" class="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
        <!-- Avatar e upload -->
        <div class="md:col-span-3 flex flex-col items-center gap-3">
          <div class="w-[200px] h-[200px] rounded-md overflow-hidden border bg-gray-100 flex items-center justify-center">
            <img v-if="previewImage" :src="previewImage" alt="Foto" class="object-cover w-full h-full" />
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-20 h-20 text-gray-400" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4Zm0 2c-3.31 0-6 2.69-6 6h12c0-3.31-2.69-6-6-6Z"/></svg>
          </div>
          <input ref="fileInput" type="file" class="hidden" @change="handleFileChange" />
          <button type="button" @click="fileInput && fileInput.click()" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Anexar</button>
          <div v-if="selectedFileName" class="text-xs text-gray-500 truncate max-w-[4.5rem]">{{ selectedFileName }}</div>
        </div>

        <!-- Campos -->
        <div class="md:col-span-9 grid grid-cols-1 md:grid-cols-6 gap-3">
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Código</label>
            <input v-model="form.id" disabled class="w-full rounded border px-3 py-2 text-sm bg-gray-100" />
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Primeiro Nome</label>
            <input v-model="form.first_name" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-3">
            <label class="text-xs text-gray-600">Sobrenome</label>
            <input v-model="form.last_name" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-1 flex items-center gap-2">
            <label class="text-xs text-gray-600">Ativo</label>
            <input type="checkbox" v-model="form.is_active" disabled />
          </div>

          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Email</label>
            <input v-model="form.email" type="email" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Login</label>
            <input v-model="form.username" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Senha</label>
            <input v-model="form.password" type="password" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Confirmar</label>
            <input v-model="form.password_confirm" type="password" class="w-full rounded border px-3 py-2 text-sm" />
          </div>

          <div class="md:col-span-3">
            <label class="text-xs text-gray-600">Telefone</label>
            <input v-model="form.phone" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-3">
            <label class="text-xs text-gray-600">CPF/CNPJ</label>
            <input v-model="form.cpf_cnpj" class="w-full rounded border px-3 py-2 text-sm" />
          </div>

          <div class="md:col-span-3">
            <label class="text-xs text-gray-600">Plano</label>
            <input :value="licensed?.plan?.name || '-'" disabled class="w-full rounded border px-3 py-2 text-sm bg-gray-100" />
          </div>
          <div class="md:col-span-3">
            <label class="text-xs text-gray-600">Cidade</label>
            <input :value="licensed?.city_lookup?.name || '-'" disabled class="w-full rounded border px-3 py-2 text-sm bg-gray-100" />
          </div>

          <div class="md:col-span-4">
            <label class="text-xs text-gray-600">Endereço</label>
            <input v-model="form.address" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Número</label>
            <input v-model="form.number" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Compl.</label>
            <input v-model="form.complement" class="w-full rounded border px-3 py-2 text-sm" />
          </div>
        </div>
      </form>
    </div>

    <!-- Footer com barra de botões -->
    <div class="px-4 py-3 border-t bg-gray-50 flex justify-end">
      <button @click="saveProfile" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">Salvar Alterações</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import api from '@/services/axios'

const user = ref({})
const licensed = ref(null)
const selectedFile = ref(null)
const selectedFileName = ref('')
const previewImage = ref('')
const fileInput = ref(null)
const form = ref({ id: '', first_name: '', last_name: '', email: '', username: '', is_active: true, phone: '', cpf_cnpj: '', password: '', password_confirm: '', address: '', number: '', complement: '' })

onMounted(async () => {
  const res = await api.get('/api/core/profile/')
  user.value = res.data
  form.value = {
    id: res.data.id,
    first_name: res.data.first_name || '',
    last_name: res.data.last_name || '',
    email: res.data.email || '',
    username: res.data.username || '',
    is_active: !res.data.is_inactive,
    phone: res.data.phone || '',
    cpf_cnpj: res.data.cpf_cnpj || '',
    address: res.data.address || '',
    number: res.data.number || '',
    complement: res.data.complement || ''
  }
  try {
    const lic = await api.get('/api/core/licensed/')
    licensed.value = lic.data?.results?.[0] || null
  } catch (e) {}
  // Define preview inicial com a imagem do usuário, se houver
  if (res.data && res.data.image_profile) {
    previewImage.value = res.data.image_profile
  }
})

const uploadImage = async () => { /* obsoleto: upload via Salvar Alterações */ }

const saveProfile = async () => {
  const fd = new FormData()
  fd.append('username', form.value.username)
  fd.append('email', form.value.email)
  fd.append('first_name', form.value.first_name || '')
  fd.append('last_name', form.value.last_name || '')
  if (form.value.password && form.value.password === form.value.password_confirm) {
    fd.append('password', form.value.password)
  }
  // sempre enviar imagem: se não selecionada, tenta usar preview atual (não obrigatório)
  if (selectedFile.value) {
    fd.append('image_profile', selectedFile.value)
  }
  await api.patch('/api/core/profile/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  alert('Perfil atualizado!')
}

function handleFileChange(e) {
  const file = (e.target && e.target.files) ? e.target.files[0] : null
  selectedFile.value = file || null
  selectedFileName.value = file ? file.name : ''
  if (file) {
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result
      previewImage.value = typeof result === 'string' ? result : ''
    }
    reader.readAsDataURL(file)
  } else {
    previewImage.value = user.value.image_profile || ''
  }
}
</script>

