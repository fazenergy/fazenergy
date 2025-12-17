<template>
  <div class="space-y-3">
    <!-- Toolbar padrão -->
    <div class="bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="refresh" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white inline-flex items-center gap-1.5">
          <RefreshCw class="w-4 h-4" />
          <span>Atualizar</span>
        </button>
        <div class="text-xs text-gray-600 ml-auto pr-1">Gerado em: {{ formatDateTime(generatedAt) }}</div>
      </div>
    </div>

    <div class="bg-white rounded border">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left bg-gray-50 border-b">
            <th class="py-2 px-2">Rotina</th>
            <th class="py-2 px-2">Descrição</th>
            <th class="py-2 px-2">Task</th>
            <th class="py-2 px-2">Agendamento</th>
            <th class="py-2 px-2">Próxima Execução</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in entries" :key="e.key" class="border-b">
            <td class="py-2 px-2 font-medium">{{ e.key }}</td>
            <td class="py-2 px-2 whitespace-pre-wrap">{{ humanDescription(e) }}</td>
            <td class="py-2 px-2 text-gray-600">{{ e.task }}</td>
            <td class="py-2 px-2"><code class="text-xs bg-gray-50 border px-1 py-0.5 rounded">{{ e.schedule }}</code></td>
            <td class="py-2 px-2">{{ formatDateTime(e.next_run) }}</td>
          </tr>
          <tr v-for="c in configs" :key="'cfg-'+c.key" class="bg-gray-50/60">
            <td class="py-2 px-2 text-xs text-gray-600">Config: {{ c.key }}</td>
            <td class="py-2 px-2">
              <label class="inline-flex items-center gap-2 text-xs">
                <input type="checkbox" :checked="c.active" @change="onToggle(c, $event)" />
                <span>{{ c.active ? 'Ativa' : 'Inativa' }}</span>
              </label>
              <div v-if="!c.active && c.disabled_reason" class="text-xs text-red-700 mt-1">Motivo: {{ c.disabled_reason }}</div>
            </td>
            <td class="py-2 px-2">
              <button @click="runNow(c.key)" class="px-2 py-1 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white">Executar Agora</button>
            </td>
            <td class="py-2 px-2" colspan="2"></td>
          </tr>
          <tr v-if="!entries.length">
            <td colspan="5" class="py-4 px-2 text-center text-gray-500">Nenhuma rotina agendada encontrada.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="text-xs text-gray-600">
      Observação: As rotinas são executadas pelo Celery Beat/Worker no backend Python. Ex.: "Celery no backend do Python rodará em dd/mm/yyyy referente à rotina tal" se baseia no campo "Próxima Execução" acima.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/axios'
import { RefreshCw } from 'lucide-vue-next'

const generatedAt = ref(null)
const entries = ref([])
const configs = ref([])

async function refresh(){
  try {
    const { data } = await api.get('/api/core/admin/schedules/')
    generatedAt.value = data?.generated_at || null
    entries.value = data?.entries || []
    // Buscar/conciliar configs salvas
    configs.value = await fetchConfigs(entries.value)
  } catch (e) {
    entries.value = []
    generatedAt.value = null
    alert('Falha ao carregar rotinas agendadas.')
  }
}

async function fetchConfigs(list){
  // Constrói uma lista mínima com active/motivo para cada key
  // Endpoint único de toggle também retorna a config atualizada; então faremos lazy-load via chamadas GET se necessário (não implementado backend GET dedicado).
  // Aqui, por simplicidade, deriva configs ativas como true por padrão e atualiza após qualquer toggle.
  return (list || []).map(e => ({ key: e.key, active: true, disabled_reason: null }))
}

function pad(n){ return String(n).padStart(2,'0') }
function formatDateTime(iso){
  if (!iso) return '-'
  const d = new Date(iso)
  return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function humanDescription(e){
  // Descrições conhecidas, com mensagem clara para admins/devs
  if (e.task === 'finance.tasks.process_scheduled_withdraws'){
    const dt = formatDateTime(e.next_run)
    return `Celery no backend do Python rodará em ${dt} referente à rotina de processamento de saques agendados.`
  }
  return e.description || '-'
}

onMounted(refresh)

async function onToggle(c, ev){
  const nextActive = ev.target.checked
  let reason = null
  if (!nextActive){
    reason = prompt('Informe o motivo da desativação desta rotina:') || ''
    if (!reason.trim()){
      ev.target.checked = true
      return
    }
  }
  try {
    const { data } = await api.post('/api/core/admin/schedules/', { action: 'toggle', key: c.key, active: nextActive, reason })
    c.active = !!data?.config?.active
    c.disabled_reason = data?.config?.disabled_reason || null
  } catch (e) {
    alert('Falha ao atualizar configuração da rotina.')
    ev.target.checked = !nextActive
  }
}

async function runNow(key){
  try {
    await api.post('/api/core/admin/schedules/', { action: 'run_now', key })
    alert('Rotina enfileirada para execução imediata.')
  } catch (e) {
    alert('Falha ao enfileirar execução da rotina.')
  }
}
</script>

<style scoped>
</style>


