<template>
  <div class="space-y-1">
    <label class="text-sm font-medium text-gray-700">{{ label }}</label>
    <slot />
  </div>
</template>

<script setup lang="ts">

defineProps<{ label: string }>()
</script>
