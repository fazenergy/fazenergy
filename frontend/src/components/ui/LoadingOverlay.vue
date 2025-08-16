<template>
  <div :class="containerClass">
    <div class="flex flex-col items-center rounded-md px-6 py-4 shadow bg-white/90">
      <div class="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin"></div>
      <p class="mt-2 text-sm text-gray-700">{{ message || 'Carregando...' }}</p>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ message?: string; fullscreen?: boolean }>()

const containerClass = computed(() =>
  props.fullscreen
    ? 'fixed inset-0 z-50 grid place-items-center bg-black/20'
    : 'absolute inset-0 z-40 grid place-items-center bg-black/10'
)
</script>






