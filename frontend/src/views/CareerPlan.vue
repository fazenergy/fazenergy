<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Plano de Carreira</h1>
      <p class="text-gray-600">Acompanhe sua evolução e próximas metas</p>
    </div>

    <!-- Cards de Resumo -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Vendas Realizadas -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-blue-800">Vendas Realizadas</h3>
          <Target class="w-5 h-5 text-blue-600" />
        </div>
        <div class="text-3xl font-bold text-blue-900">{{ stats.sales || 0 }}</div>
      </div>

      <!-- Indicações Diretas -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-green-800">Indicações Diretas</h3>
          <Users class="w-5 h-5 text-green-600" />
        </div>
        <div class="text-3xl font-bold text-green-900">{{ stats.referrals || 0 }}</div>
      </div>

      <!-- Comissões Acumuladas -->
      <div class="bg-purple-50 border border-purple-200 rounded-lg p-6 text-center">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-purple-800">Comissões Acumuladas</h3>
          <DollarSign class="w-5 h-5 text-purple-600" />
        </div>
        <div class="text-3xl font-bold text-purple-900">R$ {{ formatCurrency(stats.commissions || 0) }}</div>
      </div>

      <!-- Posição no Ranking -->
      <div class="bg-orange-50 border border-orange-200 rounded-lg p-6 text-center">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-orange-800">Posição no Ranking</h3>
          <Trophy class="w-5 h-5 text-orange-600" />
        </div>
        <div class="text-3xl font-bold text-orange-900">#{{ stats.ranking || 0 }}</div>
      </div>
    </div>

    <!-- Níveis de Carreira -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="text-gray-600">Carregando dados de carreira...</div>
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div 
        v-for="plan in careerPlans" 
        :key="plan.id"
        class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm relative"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <Trophy class="w-8 h-8" :class="getTrophyColor(plan.stage_name)" />
            <h3 class="text-2xl font-bold text-gray-900">{{ plan.stage_name }}</h3>
          </div>
          <span v-if="plan.is_current" class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">Atual</span>
        </div>
        
        <div class="mb-4">
          <p class="text-sm text-gray-600 mb-2">Requisito:</p>
          <p class="text-sm font-medium text-gray-900">
            {{ plan.required_direct_sales }} vendas + {{ plan.required_directs }} indicações diretas
          </p>
        </div>

        <!-- Progress Bar -->
        <div class="mb-4">
          <div class="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progresso</span>
            <span>{{ plan.progress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: plan.progress + '%' }"></div>
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-sm font-medium text-gray-900">Benefícios:</p>
          <p class="text-sm text-gray-600">{{ plan.reward_description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Target, Users, DollarSign, Trophy } from 'lucide-vue-next'
import api from '@/services/axios'

// Dados do usuário
const stats = ref({
  sales: 0,
  referrals: 0,
  commissions: 0,
  ranking: 0
})

const currentLevel = ref('Bronze')
const careerPlans = ref([])
const loading = ref(true)

// Função para formatar moeda
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

// Carregar dados do usuário
const loadCareerData = async () => {
  try {
    loading.value = true
    const response = await api.get('/api/core/career-data/')
    const data = response.data
    
    stats.value = data.stats
    currentLevel.value = data.current_level
    careerPlans.value = data.career_plans
  } catch (error) {
    console.error('Erro ao carregar dados de carreira:', error)
    // Fallback para dados mockados em caso de erro
    stats.value = {
      sales: 0,
      referrals: 0,
      commissions: 0,
      ranking: 0
    }
    currentLevel.value = 'Bronze'
    careerPlans.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCareerData()
})
</script>
