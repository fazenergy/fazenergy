<template>
  <button
    type="button"
    @click="toggle"
    class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
    :class="(disabled ? 'bg-gray-300' : (model ? 'bg-green-600' : 'bg-red-600'))"
    :disabled="disabled"
  >
    <span
      class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300"
      :class="model ? 'translate-x-6' : 'translate-x-1'"
    />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  disabled: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val)
})

function toggle() {
  if (props.disabled) return
  model.value = !model.value
}
</script>
