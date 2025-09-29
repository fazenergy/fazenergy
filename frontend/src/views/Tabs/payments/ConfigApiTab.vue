<template>
  <div class="mb-3 p-3 bg-white rounded">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-semibold">PIX Config API (Sicoob)</h3>
      <button @click="$emit('save')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div>
        <label class="text-xs text-gray-500">API Base URL</label>
        <input v-model.trim="form.api_base_url" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div class="md:col-span-2">
        <label class="text-xs text-gray-500">OAuth URL</label>
        <input v-model.trim="form.oauth_url" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Client ID</label>
        <input v-model.trim="form.client_id" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Client Secret</label>
        <input v-model.trim="form.client_secret" type="password" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Access Token (dev)</label>
        <input v-model.trim="form.access_token" type="password" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>

      <div>
        <label class="text-xs text-gray-500">Cert Path</label>
        <input v-model.trim="form.cert_path" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Key Path</label>
        <input v-model.trim="form.key_path" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ form: { type: Object, required: true } })
defineEmits(['save'])
</script>


