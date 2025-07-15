<template>
  <select
    v-bind="$attrs"
    :class="[
      'w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm',
      'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
      'disabled:opacity-50 disabled:cursor-not-allowed'
    ]"
  >
    <slot />
  </select>
</template>
