<template>
  <div class="p-3 bg-white rounded">
    <h3 class="text-sm font-semibold mb-3">Configurações de E-mail (SMTP)</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div>
        <label class="text-xs text-gray-500">Servidor SMTP</label>
        <input v-model.trim="smtp.smtp_host" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Porta SMTP</label>
        <input v-model.number="smtp.smtp_port" type="number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Usuário SMTP</label>
        <input v-model.trim="smtp.smtp_user" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Senha APP</label>
        <input v-model.trim="smtp.smtp_password" type="password" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Remetente Padrão</label>
        <input v-model.trim="smtp.default_from_email" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Destinatário de Teste</label>
        <input v-model.trim="smtp.test_recipient" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div class="flex items-center gap-4">
        <label class="inline-flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="smtp.use_ssl" /> Usar SSL
        </label>
        <label class="inline-flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="smtp.use_tls" /> Usar TLS
        </label>
      </div>
    </div>
    <div class="mt-3 flex gap-2 justify-end">
      <button @click="saveSMTP" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Salvar Configuração</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/axios'

const smtp = ref({
  smtp_host: '', smtp_port: 465, smtp_user: '', smtp_password: '',
  default_from_email: '', test_recipient: '', use_ssl: true, use_tls: false
})

async function fetchSMTP() {
  try {
    const { data } = await api.get('/api/notifications/config/')
    if (data) smtp.value = data
  } catch {}
}

async function saveSMTP() {
  const payload = { ...smtp.value }
  if (payload.id) {
    await api.put(`/api/notifications/config/${payload.id}/`, payload)
  } else {
    await api.post('/api/notifications/config/', payload)
  }
}

onMounted(fetchSMTP)
</script>


