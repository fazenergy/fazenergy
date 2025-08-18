<!-- src/views/Dashboard.vue -->
<!-- src/views/Dashboard.vue -->
<template>
<div>
   <!-- ✅ Botão visível só para licenciados -->
    <button
      v-if="isLicensed"
      @click="goToPreRegister"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    >
      Cadastrar Licenciado
    </button>
</div>
<div class="flex">
    <div class="flex-1">
    <main class="p-6 space-y-6">

    <!-- Cards principais -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card v-for="(c, idx) in cards" :key="c.key" :className="cardClass(c, idx)">
         <template #title><div>{{ c.title }}</div></template>
         <template #content><div><p class="text-2xl font-bold">{{ c.value }}</p></div></template>
         <template #description><div v-if="c.delta">{{ c.delta }}</div></template>
         <template #icon><UserPlus class="w-5 h-5" /></template>
      </Card>
    </div>

  <!-- Ações rápidas, relatórios e configurações -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Ações Rápidas</h2>
            <button v-for="qa in quickActions" :key="qa.route" @click="router.push(qa.route)" class="block w-full p-2 bg-blue-500 text-white rounded mb-2">{{ qa.label }}</button>
          </div>

          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Relatórios</h2>
            <p>Relatórios aqui...</p>
          </div>

          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Configurações</h2>
            <p>Configurações aqui...</p>
          </div>
        </div>

        <div class="border p-4 rounded">
          <h2 class="font-bold mb-2">Atividade Recente</h2>
          <ul class="space-y-2">
            <li>🔵 Novo afiliado cadastrado</li>
            <li>🔵 Comissão processada</li>
            <li>🔵 Nova venda registrada</li>
          </ul>
        </div>
      </main>
    </div>
  </div>
  
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { computed, ref, onMounted } from 'vue'
import Card from '@/components/ui/Card.vue'
import { UserPlus, DollarSign, TrendingUp, UserCheck } from 'lucide-vue-next'
import api from '@/services/axios'

const auth = useAuthStore()
const router = useRouter()

// Exemplo: se você salva grupos no `auth.user`
const isLicensed = computed(() => {
  return auth.user?.groups?.includes('Licenciado')
})

function goToPreRegister() {
  router.push('/preRegister')
}

const cards = ref([])
const quickActions = ref([])

async function fetchDashboard() {
  const { data } = await api.get('/api/core/dashboard/')
  cards.value = data?.cards || []
  quickActions.value = data?.quickActions || []
}

onMounted(fetchDashboard)

function cardClass(card, index) {
  const base = 'bg-gradient-to-r text-white shadow-lg hover:scale-[1.01] transition-transform'
  const byKey = {
    total_licensed: 'from-blue-500 to-blue-600',
    active_affiliates: 'from-emerald-500 to-emerald-600',
    roots_count: 'from-purple-500 to-purple-600',
    network_edges: 'from-orange-500 to-orange-600',
    directs: 'from-blue-500 to-blue-600',
    team_size: 'from-purple-500 to-purple-600',
    active_team: 'from-emerald-500 to-emerald-600',
    career: 'from-orange-500 to-orange-600',
  }
  const palette = [
    'from-blue-500 to-blue-600',
    'from-emerald-500 to-emerald-600',
    'from-purple-500 to-purple-600',
    'from-orange-500 to-orange-600',
  ]
  const grad = byKey[card?.key] || palette[index % palette.length]
  return `${base} ${grad}`
}
</script>
