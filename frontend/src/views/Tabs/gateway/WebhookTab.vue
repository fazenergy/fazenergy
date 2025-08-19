<template>
  <div class="p-3 bg-white rounded">
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-sm font-semibold">Webhook</h3>
      <button @click="$emit('save')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
      <div>
        <label class="text-xs text-gray-500">Token</label>
        <input v-model.trim="form.webhook_token" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">User</label>
        <input v-model.trim="form.webhook_user" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Password</label>
        <input v-model.trim="form.webhook_password" type="password" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-500">Secret</label>
        <input v-model.trim="form.webhook_secret" class="w-full border rounded px-2 py-1 h-8 text-sm" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ form: { type: Object, required: true } })
defineEmits(['save'])
</script>


