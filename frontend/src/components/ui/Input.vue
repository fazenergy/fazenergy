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
    :value="modelValue ?? ''"
    @input="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script setup>
import { computed, useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: [String, Number],
  mask: String
})

const attrs = useAttrs()
const isReadonly = computed(() => attrs.readonly !== undefined && attrs.readonly !== false)

const classes = computed(() => [
  'w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm',
  // Background depende do modo leitura
  isReadonly.value ? 'bg-gray-100' : 'bg-white',
  // Estados de foco: suaviza quando readonly
  isReadonly.value ? 'focus:outline-none focus:ring-0 focus:border-gray-300 cursor-not-allowed' : 'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
  // Disabled nativo
  'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-100'
])
</script>