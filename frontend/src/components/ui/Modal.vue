<template>
  <div v-if="modelValue" class="fixed inset-0 z-50">
    <div class="absolute inset-0 bg-black/50" @click="$emit('update:modelValue', false)"></div>
    <div class="absolute inset-0 grid place-items-center p-4">
      <div class="w-full max-w-5xl bg-white rounded-lg shadow-xl overflow-hidden">
        <div :class="['flex items-center justify-between px-4 py-3', headerBlue ? 'bg-blue-600 text-white' : '', !noHeaderBorder ? 'border-b' : '']">
          <h3 class="text-sm font-semibold">
            <slot name="title">Modal</slot>
          </h3>
          <button :class="['', headerBlue ? 'text-white/90 hover:text-white' : 'text-gray-500 hover:text-gray-700']" @click="$emit('update:modelValue', false)">✕</button>
        </div>
        <div class="px-4 pb-4 pt-0 max-h-[80vh] overflow-auto">
          <slot />
        </div>
        <div v-if="$slots.footer" class="px-4 py-3 border-t bg-gray-50">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  headerBlue: { type: Boolean, default: false },
  noHeaderBorder: { type: Boolean, default: false }
})
defineEmits(['update:modelValue'])
</script>


