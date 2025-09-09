<template>
  <div class="space-y-4">
    <!-- Painel Único: Cabeçalho + Conteúdo -->
    <div class="bg-white rounded border">
      <!-- Cabeçalho -->
      <div class="p-3 flex items-start md:items-center justify-between gap-4">
        <div>
          <h3 class="text-sm font-semibold">Configurações de Rede Multinível</h3>
        </div>
        <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
      </div>

      <!-- Conteúdo: Toggles -->
      <div class="p-4 border-t">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Compressão Dinâmica -->
          <div class="space-y-1">
            <div class="flex items-start md:items-center gap-3">
              <div>
                <div class="text-sm font-medium">Compressão Dinâmica</div>
                <div class="text-[12px] text-gray-500">Quando ativa, inativos são pulados na árvore para cálculo.</div>
              </div>
              <label class="inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="form.dynamic_compression" class="sr-only peer">
                <div class="w-10 h-5 bg-gray-300 rounded-full peer peer-checked:bg-green-500 relative transition-colors">
                  <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transform peer-checked:translate-x-5 transition-transform"></div>
                </div>
              </label>
            </div>
          </div>

          <!-- Ativar Bonificação -->
          <div class="space-y-1">
            <div class="flex items-start md:items-center gap-3">
              <div>
                <div class="text-sm font-medium">Ativar Bonificação</div>
                <div class="text-[12px] text-gray-500">Habilita o sistema de bônus e recompensas para a rede.</div>
              </div>
              <label class="inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="form.enable_rewards" class="sr-only peer">
                <div class="w-10 h-5 bg-gray-300 rounded-full peer peer-checked:bg-green-500 relative transition-colors">
                  <div class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transform peer-checked:translate-x-5 transition-transform"></div>
                </div>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Conteúdo: Limites -->
      <div class="p-4 border-t">
        <div class="text-base font-semibold mb-3">Limites da Rede</div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="text-xs text-gray-500">Níveis Máximos de Comissão</label>
            <select v-model.number="form.max_commission_levels" class="w-full border rounded px-2 py-1 h-8 text-sm">
              <option v-for="n in levels" :key="n" :value="n">{{ n }} níveis</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerta fora do box -->
    <div class="p-3 rounded border border-amber-300 bg-amber-50 text-amber-800 text-[12px]">
      Importante: a compressão é automaticamente desativada para usuários inativos.
    </div>
  </div>
</template>

<script setup>
// Componente de configurações da Rede.
// Lê/escreve os dados via store central de configurações.
import { ref, onMounted, watch } from 'vue'
import { useSettingsStore } from '@/store/settings'

const levels = [3,4,5,6,7,8,9,10]
// Instância do store de configurações
const settingsStore = useSettingsStore()

// Estado local do formulário (para edição desacoplada do store)
const form = ref({ dynamic_compression: true, enable_rewards: true, max_commission_levels: 5 })

// Carrega do store na montagem do componente
onMounted(() => {
  settingsStore.loadFromStorage()
  form.value = { ...form.value, ...settingsStore.settings.network }
})

// Sempre que o form mudar, opcionalmente poderíamos sincronizar live.
// Vamos manter apenas na ação de Gravar para espelhar o comportamento das outras abas.

function save() {
  // Atualiza o bloco "network" no store e persiste tudo em localStorage
  settingsStore.setNetwork({ ...form.value })
  settingsStore.saveToStorage()
  alert('Configurações de rede salvas.')
}
</script>


