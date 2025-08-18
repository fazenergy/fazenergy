<template>
  <div class="space-y-0">
    <label class="text-[13px] font-medium text-gray-700 leading-tight">
      {{ label }}
      <span v-if="error" class="ml-1 text-red-500 text-xs font-normal">* {{ error }}</span>
    </label>
    <slot />
  </div>
  
</template>

<script setup lang="ts">
defineProps<{ label: string; error?: string }>()
</script>
