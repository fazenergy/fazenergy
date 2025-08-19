<template>
  <div class="mb-3 p-3 bg-white rounded">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-semibold">Gateway Configs</h3>
      <button @click="$emit('save')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
    </div>
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
      <div>
        <label class="text-xs text-gray-500">Token API</label>
        <input v-model.trim="form.api_token" type="password" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div class="md:col-span-2">
        <label class="text-xs text-gray-500">API URL</label>
        <input v-model.trim="form.api_url" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Dev URL (hint)</label>
        <input v-model.trim="form.dev_url_hint" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Postback URL</label>
        <input v-model.trim="form.postback_url" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Redirect URL</label>
        <input v-model.trim="form.redirect_url" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ form: { type: Object, required: true } })
defineEmits(['save'])
</script>


