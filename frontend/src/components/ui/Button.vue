<template>
  <button
    v-bind="$attrs"
    :class="[
      'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium',
      variantClass,
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'focus:outline-none focus:ring-2 focus:ring-offset-2'
    ]"
  >
    <slot />
  </button>
 </template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }
})

const variantClass = computed(() => {
  if (props.variant === 'success') {
    return 'text-white bg-gradient-to-b from-[#62c462] to-[#51a351] hover:from-[#5cb85c] hover:to-[#4cae4c] border border-[#4cae4c] focus:ring-[#4cae4c]'
  }
  return 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
})
</script>
