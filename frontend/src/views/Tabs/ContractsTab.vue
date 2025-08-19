<template>
  <div class="space-y-3">
    <div class="flex border-b mb-2 space-x-2">
      <button :class="['px-4 py-2 rounded-t', innerTab==='Lexo API' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="innerTab='Lexo API'">Lexo API</button>
      <button :class="['px-4 py-2 rounded-t', innerTab==='Templates' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="innerTab='Templates'">Templates</button>
    </div>
    <component :is="current" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LexoTab from './LexoTab.vue'
import ContractTemplatesTab from './ContractTemplatesTab.vue'

const innerTab = ref('Lexo API')
const current = computed(() => innerTab.value === 'Lexo API' ? LexoTab : ContractTemplatesTab)
</script>


