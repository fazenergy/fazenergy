<template>
  <div class="space-y-3">
    <div class="flex border-b mb-2 space-x-2">
      <button :class="['px-4 py-2 rounded-t', active==='SMTP' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='SMTP'">SMTP</button>
      <button :class="['px-4 py-2 rounded-t', active==='Templates' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Templates'">Templates</button>
    </div>
    <component :is="current" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import NotificationsTemplatesTab from './NotificationsTemplatesTab.vue'
import SmtpTab from './SmtpTab.vue'

const active = ref('Templates')
const current = computed(() => active.value === 'SMTP' ? SmtpTab : NotificationsTemplatesTab)
</script>

