<!-- src/components/ui/Input.vue -->
<template>
  <input
    v-if="mask"
    v-mask="mask"
    v-bind="$attrs"
    :class="classes"
  />
  <input
    v-else
    v-bind="$attrs"
    :class="classes"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const classes = computed(() => [
  'w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm',
  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
  'disabled:opacity-50 disabled:cursor-not-allowed'
])

</script>
