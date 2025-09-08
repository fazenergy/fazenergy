<template>
  <div class="space-y-4">
    <!-- Painel único -->
    <div class="bg-white rounded border">
      <!-- Cabeçalho -->
      <div class="p-3 flex items-start md:items-center justify-between gap-4">
        <div>
          <h3 class="text-sm font-semibold">Configurações de Pagamentos</h3>
          <p class="text-[11px] text-gray-500">Parâmetros para solicitação de saque e prazos.</p>
        </div>
        <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
      </div>

      <!-- Conteúdo -->
      <div class="p-4 border-t">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-gray-500">Valor Mínimo para Saque (R$)</label>
            <input v-model.number="form.withdraw_min_value" type="number" step="0.01" min="0" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Taxa de Saque a ser deduzida (%)</label>
            <input v-model.number="form.withdraw_fee_percent" type="number" step="0.01" min="0" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Dia Limite para Solicitar Saque</label>
            <input v-model.number="form.request_deadline_day" type="number" min="1" max="31" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Dia Limite de Pagamento</label>
            <input v-model.number="form.payment_deadline_day" type="number" min="1" max="31" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
        </div>
      </div>
    </div>

    <!-- Texto dinâmico -->
    <div class="p-3 rounded border border-sky-300 bg-sky-50 text-sky-800 text-[12px]">
      Se licenciado solicitar até o dia <strong>{{ form.request_deadline_day }}</strong> então temos até o dia <strong>{{ form.payment_deadline_day }}</strong> para efetuar o pagamento.
    </div>
  </div>
</template>

<script setup>
// Aba Pagamentos: integra com o store para carregar e salvar.
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/store/settings'

const settingsStore = useSettingsStore()
const form = ref({ withdraw_min_value: 0, withdraw_fee_percent: 0, request_deadline_day: 10, payment_deadline_day: 20 })

onMounted(() => {
  settingsStore.loadFromStorage()
  form.value = { ...form.value, ...settingsStore.settings.payments }
})

function save() {
  settingsStore.setPayments({ ...form.value })
  settingsStore.saveToStorage()
  alert('Configurações de pagamentos salvas.')
}
</script>


