<!-- src/views/Settings.vue -->
<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-2">Configurações do Sistema</h1>
    <p class="text-gray-600 mb-6">Gerencie as configurações globais do sistema MMN</p>

    <!-- Abas -->
    <div class="flex border-b mb-4 space-x-2">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        :class="[
          'px-4 py-2 rounded-t',
          activeTab === tab
            ? 'bg-green-600 text-white border border-b-0'
            : 'bg-gray-100 hover:bg-gray-200'
        ]"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Conteúdo da Aba -->
    <div class="border rounded p-4 bg-white">
      <component :is="currentTabComponent" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PlansTab from './Tabs/PlansTab.vue'
import CareerPlansTab from './Tabs/CareerPlansTab.vue'
import NotificationsTab from './Tabs/NotificationsTab.vue'
import GatewayTab from './Tabs/GatewayTab.vue'
import ContractsTab from './Tabs/ContractsTab.vue'
import GeneralTab from './Tabs/GeneralTab.vue'

const GenericTab = {
  template: `<div class="text-gray-500">Aba <strong>{{ tab }}</strong> ainda não implementada.</div>`,
  props: ['tab']
}

const tabs = ['Geral', 'Comissões', 'Gateway', 'Planos', 'Planos de Carreira', 'Notificações', 'Webhooks', 'APIs', 'Contratos']
const activeTab = ref('Planos') // já abre na aba Planos

const currentTabComponent = computed(() => {
  switch (activeTab.value) {
    case 'Planos':
      return PlansTab
    case 'Geral':
      return GeneralTab
    case 'Planos de Carreira':
      return CareerPlansTab
    case 'Gateway':
      return GatewayTab
    case 'Notificações':
      return NotificationsTab
    // depois você pode registrar outros tabs aqui
    default:
      if (activeTab.value === 'Contratos') return ContractsTab
      return GenericTab
  }
})

// import { ref, computed } from 'vue'

// // Importe cada aba como componente separado:
// // import GeneralTab from './tabs/GeneralTab.vue'
// import PlansTab from './Tabs/PlansTab.vue'  // ✅ Sua nova aba!
// // import CommissionsTab from './tabs/CommissionsTab.vue'
// // import PaymentsTab from './tabs/PaymentsTab.vue'
// // import NotificationsTab from './tabs/NotificationsTab.vue'
// // import WebhooksTab from './tabs/WebhooksTab.vue'
// // import APIsTab from './tabs/APIsTab.vue'
// // import ContractsTab from './tabs/ContractsTab.vue'


// const tabs = [
//   // 'Geral',
//   'Planos',
//   // 'Comissões',
//   // 'Pagamentos',
//   // 'Notificações',
//   // 'Webhooks',
//   // 'APIs',
//   // 'Contratos' 
// ]

// const activeTab = ref('Geral')

// const currentTabComponent = computed(() => {
//   switch (activeTab.value) {
//     // case 'Geral': return GeneralTab
//     case 'Planos': return PlansTab
//     // case 'Comissões': return CommissionsTab
//     // case 'Pagamentos': return PaymentsTab
//     // case 'Notificações': return NotificationsTab
//     // case 'Webhooks': return WebhooksTab
//     // case 'APIs': return APIsTab
//     // case 'Contratos': return ContractsTab
//     default: return GeneralTab
//   }
// })
</script>

<style scoped>
/* Exemplo: fundo da aba ativa */
</style>
