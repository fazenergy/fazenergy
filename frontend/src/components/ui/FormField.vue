<template>
  <div class="space-y-1">
    <label class="text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="error" class="ml-1 text-red-500 text-xs font-normal">* {{ error }}</span>
    </label>
    <slot />
  </div>
  
</template>

<script setup lang="ts">
defineProps<{ label: string; error?: string }>()
</script>
