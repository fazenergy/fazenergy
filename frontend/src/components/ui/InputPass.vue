<template>
  <div class="relative">
    <input
      v-bind="$attrs"
      :type="show ? 'text' : 'password'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      autocomplete="off"
    />
    <button
      type="button"
      class="absolute right-1 top-1/2 -translate-y-1/2 bg-white border border-gray-200 rounded px-1 py-0.5 flex items-center justify-center shadow-sm hover:bg-gray-100 focus:outline-none"
      style="height: 28px; width: 28px;"
      @click="show = !show"
      tabindex="-1"
      aria-label="Mostrar/ocultar senha"
    >
      <!-- Olho aberto -->
      <svg v-if="show" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="12" r="3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <!-- Olho riscado -->
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path d="M17.94 17.94A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-7 0-1.657.402-3.22 1.125-4.575M3 3l18 18" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M1 12s4-7 11-7c2.21 0 4.21.72 5.94 1.94M21 21l-6.36-6.36" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="12" r="3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineProps({ modelValue: [String, Number] })
const show = ref(false)
</script>