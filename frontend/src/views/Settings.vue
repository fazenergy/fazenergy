<!-- src/views/Settings.vue -->
<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-2">Configurações do Sistema</h1>
    <p class="text-gray-600 mb-6">Gerencie as configurações globais do sistema MMN</p>

    <!-- Abas + botão Info -->
    <div class="flex items-center justify-between border-b mb-4">
      <div class="flex space-x-2">
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
      <button @click="openInfo" class="inline-flex items-center justify-center w-8 h-8 rounded text-blue-600 hover:text-blue-700 border border-blue-200 hover:border-blue-300 shadow-sm" title="Sobre esta aba">
        <Info class="w-4 h-4" />
      </button>
    </div>

    <!-- Conteúdo da Aba -->
    <div class="border rounded p-4 bg-white">
      <component :is="currentTabComponent" />
    </div>

    <!-- Modal de Info -->
    <Modal v-model="showInfo" :header-blue="true" max-width="max-w-lg">
      <template #title>{{ activeTab }}</template>
      <div class="text-sm text-gray-700 whitespace-pre-line">{{ infoMessage }}</div>
      <template #footer>
        <div class="flex items-center justify-end gap-2">
          <button class="px-3 py-1.5 rounded border" @click="showInfo=false">Fechar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Modal from '@/components/ui/Modal.vue'
import { Info } from 'lucide-vue-next'
import PlansTab from './Tabs/PlansTab.vue'
import CareerPlansTab from './Tabs/CareerPlansTab.vue'
import NotificationsTab from './Tabs/NotificationsTab.vue'
import GatewayTab from './Tabs/GatewayTab.vue'
import ContractsTab from './Tabs/ContractsTab.vue'
import GeneralTab from './Tabs/GeneralTab.vue'
import NetworkTab from './Tabs/NetworkTab.vue'
import PaymentsTab from './Tabs/PaymentsTab.vue'

const GenericTab = {
  template: `<div class="text-gray-500">Aba <strong>{{ tab }}</strong> ainda não implementada.</div>`,
  props: ['tab']
}

const tabs = ['Geral', 'Rede', 'Pagamentos', 'Gateway', 'Planos', 'Planos de Carreira', 'Notificações', 'Contratos']
const activeTab = ref('Planos') // já abre na aba Planos

const currentTabComponent = computed(() => {
  switch (activeTab.value) {
    case 'Planos':
      return PlansTab
    case 'Geral':
      return GeneralTab
    case 'Rede':
      return NetworkTab
    case 'Pagamentos':
      return PaymentsTab
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

// Botão Info
const showInfo = ref(false)
const infoMap = {
  'Geral': 'Informações institucionais, contatos e logos da empresa para uso em telas e relatórios.',
  'Rede': 'Parâmetros do MMN: compressão dinâmica, habilitações e níveis de comissionamento.',
  'Pagamentos': 'Regras de saque (Configurações) e integração PIX Sicoob (Config API e Webhook).',
  'Gateway': 'Integração com o gateway Pagar.me para venda do plano anual (links, postback, redirect).',
  'Planos': 'Cadastro e manutenção dos planos MMN utilizados nas adesões e cálculos.',
  'Planos de Carreira': 'Etapas de carreira, requisitos (pontos, diretos, vendas) e progressão.',
  'Notificações': 'Configuração de SMTP e templates de e-mail com envio de teste.',
  'Contratos': 'Integração com Lexo Legal: configurações e templates de contrato.'
}
const infoMessage = computed(() => infoMap[activeTab.value] || 'Sem descrição para esta aba.')
function openInfo(){ showInfo.value = true }

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
