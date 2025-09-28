<template>
  <div v-if="modelValue" class="fixed inset-0 z-50">
    <div class="fixed inset-0 bg-black/50" @click="$emit('update:modelValue', false)"></div>
    <div class="absolute inset-0 grid justify-center items-start p-4 md:p-6">
      <div :class="['w-full', maxWidth, 'bg-white rounded-lg shadow-xl overflow-hidden mt-6 md:mt-8 mb-6']">
        <div :class="['flex items-center justify-between px-4 py-3', headerBlue ? 'bg-blue-600 text-white' : '', !noHeaderBorder ? 'border-b' : '']">
          <h3 class="text-sm font-semibold">
            <slot name="title">Modal</slot>
          </h3>
          <button :class="['', headerBlue ? 'text-white/90 hover:text-white' : 'text-gray-500 hover:text-gray-700']" @click="$emit('update:modelValue', false)">✕</button>
        </div>
        <div class="px-4 pb-5 pt-[15px] max-h-[calc(100vh-160px)] overflow-auto">
          <slot />
        </div>
        <div v-if="$slots.footer" class="px-4 py-2 border-t bg-gray-50">
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
  noHeaderBorder: { type: Boolean, default: false },
  // Define a largura máxima do modal (Tailwind class), ex.: 'max-w-7xl'
  maxWidth: { type: String, default: 'max-w-5xl' }
})
defineEmits(['update:modelValue'])
</script>


