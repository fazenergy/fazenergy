<!-- src/components/ui/Card.vue -->
<template>
  <div
    class="rounded-lg border bg-card text-card-foreground shadow-sm p-4"
    :class="className"
  >
    <!-- Linha principal: textos + ícone -->
    <div class="flex justify-between items-center">
      <!-- Bloco de texto -->
      <div>
        <h3 v-if="$slots.title" class="text-lg font-semibold mb-1">
          <slot name="title" />
        </h3>
        <div v-if="$slots.content">
          <slot name="content" />
        </div>
        <p v-if="$slots.description" class="text-xs text-white/80 mt-1">
          <slot name="description" />
        </p>
      </div>

      <!-- Ícone (direita, centralizado) -->
      <div v-if="$slots.icon" class="bg-white/20 rounded p-3">
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
  }
})
</script>
