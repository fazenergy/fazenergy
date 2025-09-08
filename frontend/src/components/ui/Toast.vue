<template>
  <transition name="fade">
    <div v-if="modelValue" :class="['fixed top-4 right-4 z-50 min-w-[240px] max-w-sm rounded shadow-lg px-4 py-3 text-sm',
      type==='success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white']">
      {{ message }}
    </div>
  </transition>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  message: { type: String, default: '' },
  type: { type: String, default: 'success' },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.fade-enter-active,.fade-leave-active{transition:opacity .2s ease}
.fade-enter-from,.fade-leave-to{opacity:0}
</style>


