<!-- src/components/ui/Card.vue -->
<template>
  <div
    class="rounded-lg border bg-white text-gray-900 shadow-sm p-4 flex items-stretch"
    :class="className"
  >
    <!-- Linha principal: textos + ícone -->
    <div class="flex justify-between items-center w-full">
      <!-- Bloco de texto -->
      <div>
        <h3 v-if="$slots.title" class="text-base font-semibold mb-1">
          <slot name="title" />
        </h3>
        <div v-if="$slots.content">
          <slot name="content" />
        </div>
        <p v-if="$slots.description" class="text-xs mt-1" :class="descriptionClass">
          <slot name="description" />
        </p>
      </div>

      <!-- Ícone (direita, centralizado) -->
      <div v-if="$slots.icon" :class="[iconBgClass, 'rounded p-2']">
        <slot name="icon" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  className: {
    type: String,
    default: ''
  },
  iconBgClass: {
    type: String,
    default: 'bg-white/20'
  },
  descriptionClass: {
    type: String,
    default: 'text-white/80'
  }
})
</script>
