<template>
  <button
    v-bind="$attrs"
    :class="[
      'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium',
      'bg-blue-600 text-white hover:bg-blue-700',
      'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
    ]"
  >
    <slot />
  </button>
</template>
