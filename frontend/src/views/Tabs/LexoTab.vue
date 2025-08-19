<template>
  <div class="p-3 bg-white rounded">
    <h3 class="text-sm font-semibold mb-3">Configurações API Lexo</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div>
        <label class="text-xs text-gray-500">Lexo URL</label>
        <input v-model.trim="form.lexio_url" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Lexo Token</label>
        <input v-model.trim="form.lexio_token" type="password" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Parte Empresa (nome)</label>
        <input v-model.trim="form.signer_name_partner" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Parte Empresa (e-mail)</label>
        <input v-model.trim="form.signer_mail_partner" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Testemunha (nome)</label>
        <input v-model.trim="form.signer_name_testmon" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Testemunha (e-mail)</label>
        <input v-model.trim="form.signer_mail_testmon" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
    </div>
    <div class="mt-3 flex justify-end gap-2">
      <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/axios'

const form = ref({})

async function fetchConfig() {
  try {
    const { data } = await api.get('/api/contracts/config/')
    if (data) form.value = data
  } catch {}
}

async function save() {
  const payload = { ...form.value }
  if (payload.id) {
    await api.put(`/api/contracts/config/${payload.id}/`, payload)
  } else {
    await api.post('/api/contracts/config/', payload)
  }
}

onMounted(fetchConfig)
</script>


