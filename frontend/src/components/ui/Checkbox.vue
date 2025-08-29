<template>
  <input
    type="checkbox"
    v-bind="$attrs"
    :class="[
      'h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500'
    ]"
    :checked="model"
    @change="onChange"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'


const props = defineProps({
  modelValue: Boolean
})
const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: val => emit('update:modelValue', val)
})

function onChange(e: Event) {
  const target = e.target as HTMLInputElement
  model.value = !!target.checked
}
</script>