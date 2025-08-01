<template>
  <input
    v-bind="$attrs"
    :class="classes"
    :value="modelValue"
    v-if="mask"
    v-mask="mask"
    @input="$emit('update:modelValue', $event.target.value)"
  />
  <input
    v-else
    v-bind="$attrs"
    :class="classes"
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script setup>
import { computed } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: [String, Number],
  mask: String
})

const classes = computed(() => [
  'w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm',
  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
  'disabled:opacity-50 disabled:cursor-not-allowed'
])
</script>