<template>
  <textarea
    ref="ta"
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
    class="w-full font-mono border rounded px-2 py-2 text-xs min-h-[260px]"
    spellcheck="false"
  />
</template>

<script setup>
defineProps({ modelValue: { type: String, default: '' } })
</script>


