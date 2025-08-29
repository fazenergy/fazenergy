<template>
  <div class="space-y-0">
    <label class="text-[13px] font-medium text-gray-700 leading-tight inline-flex items-center gap-1">
      <span>{{ label }}</span>
      <span v-if="required" class="text-red-500" title="Obrigatório">*</span>
      <span v-if="valid" class="text-emerald-600 text-xs" title="Válido">✔</span>
      <span v-if="error" class="ml-1 text-red-500 text-xs font-normal">{{ error }}</span>
    </label>
    <slot />
  </div>
  
</template>

<script setup lang="ts">
defineProps<{ label: string; error?: string; required?: boolean; valid?: boolean }>()
</script>
