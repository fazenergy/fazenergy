<template>
  <div class="space-y-6">
    <!-- ======================================== -->
    <!-- HEADER DA PÁGINA -->
    <!-- ======================================== -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Relatórios</h1>
        <p class="text-gray-600">Análise completa do desempenho da rede</p>
      </div>
      <!-- Botão de exportação do relatório -->
      <button 
        @click="exportReport" 
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-flex items-center gap-2"
      >
        <Download class="w-4 h-4" />
        Exportar Relatório
      </button>
    </div>

    <!-- ======================================== -->
    <!-- CARDS DE RESUMO - MÉTRICAS PRINCIPAIS -->
    <!-- ======================================== -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Card 1: Faturamento Total -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <!-- Ícone do faturamento -->
          <div class="p-3 bg-green-100 rounded-lg">
            <DollarSign class="w-6 h-6 text-green-600" />
          </div>
        </div>
        <div class="mb-2">
          <h3 class="text-sm font-medium text-gray-600">Faturamento Total</h3>
          <p class="text-2xl font-bold text-gray-900">R$ {{ formatCurrency(stats.totalRevenue) }}</p>
        </div>
        <!-- Indicador de crescimento -->
        <div class="flex items-center text-sm">
          <TrendingUp class="w-4 h-4 text-green-500 mr-1" />
          <span class="text-green-600 font-medium">+{{ stats.revenueGrowth }}%</span>
          <span class="text-gray-500 ml-1">em relação ao mês passado</span>
        </div>
      </div>

      <!-- Card 2: Comissões Pagas -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <!-- Ícone das comissões -->
          <div class="p-3 bg-blue-100 rounded-lg">
            <BarChart3 class="w-6 h-6 text-blue-600" />
          </div>
        </div>
        <div class="mb-2">
          <h3 class="text-sm font-medium text-gray-600">Comissões Pagas</h3>
          <p class="text-2xl font-bold text-gray-900">R$ {{ formatCurrency(stats.commissionsPaid) }}</p>
        </div>
        <!-- Indicador de crescimento -->
        <div class="flex items-center text-sm">
          <TrendingUp class="w-4 h-4 text-green-500 mr-1" />
          <span class="text-green-600 font-medium">+{{ stats.commissionsGrowth }}%</span>
          <span class="text-gray-500 ml-1">em relação ao mês passado</span>
        </div>
      </div>

      <!-- Card 3: Afiliados Ativos -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <!-- Ícone dos afiliados -->
          <div class="p-3 bg-purple-100 rounded-lg">
            <Users class="w-6 h-6 text-purple-600" />
          </div>
        </div>
        <div class="mb-2">
          <h3 class="text-sm font-medium text-gray-600">Afiliados Ativos</h3>
          <p class="text-2xl font-bold text-gray-900">{{ stats.activeAffiliates }}</p>
        </div>
        <!-- Indicador de crescimento -->
        <div class="flex items-center text-sm">
          <TrendingUp class="w-4 h-4 text-green-500 mr-1" />
          <span class="text-green-600 font-medium">+{{ stats.affiliatesGrowth }}%</span>
          <span class="text-gray-500 ml-1">em relação ao mês passado</span>
        </div>
      </div>

      <!-- Card 4: Novos Cadastros -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <!-- Ícone dos cadastros -->
          <div class="p-3 bg-orange-100 rounded-lg">
            <Calendar class="w-6 h-6 text-orange-600" />
          </div>
        </div>
        <div class="mb-2">
          <h3 class="text-sm font-medium text-gray-600">Novos Cadastros</h3>
          <p class="text-2xl font-bold text-gray-900">{{ stats.newRegistrations }}</p>
        </div>
        <!-- Indicador de crescimento -->
        <div class="flex items-center text-sm">
          <TrendingUp class="w-4 h-4 text-green-500 mr-1" />
          <span class="text-green-600 font-medium">+{{ stats.registrationsGrowth }}%</span>
          <span class="text-gray-500 ml-1">em relação ao mês passado</span>
        </div>
      </div>
    </div>

    <!-- ======================================== -->
    <!-- TABELAS DE DADOS DETALHADOS -->
    <!-- ======================================== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Tabela 1: Desempenho Mensal -->
      <div class="bg-white border border-gray-200 rounded-lg shadow-sm">
        <!-- Cabeçalho da tabela -->
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Desempenho Mensal</h3>
          <p class="text-sm text-gray-600">Últimos 4 meses</p>
        </div>
        <!-- Tabela responsiva -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <!-- Cabeçalho das colunas -->
            <thead class="bg-blue-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mês</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Faturamento</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comissões</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Afiliados</th>
              </tr>
            </thead>
            <!-- Dados da tabela -->
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(month, index) in monthlyPerformance" :key="index" :class="index % 2 === 0 ? 'bg-white' : 'bg-gray-50'">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ month.month }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">R$ {{ formatCurrency(month.revenue) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">R$ {{ formatCurrency(month.commissions) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ month.affiliates }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tabela 2: Top Afiliados -->
      <div class="bg-white border border-gray-200 rounded-lg shadow-sm">
        <!-- Cabeçalho da tabela -->
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">Top Afiliados</h3>
          <p class="text-sm text-gray-600">Melhores performadores do mês</p>
        </div>
        <!-- Tabela responsiva -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <!-- Cabeçalho das colunas -->
            <thead class="bg-blue-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendas</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comissão</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nível</th>
              </tr>
            </thead>
            <!-- Dados da tabela -->
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(affiliate, index) in topAffiliates" :key="index" :class="index % 2 === 0 ? 'bg-white' : 'bg-gray-50'">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ affiliate.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ affiliate.sales }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">R$ {{ formatCurrency(affiliate.commission) }}</td>
                <!-- Badge do nível de carreira -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getLevelBadgeClass(affiliate.level)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ affiliate.level }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// ========================================
// IMPORTAÇÕES
// ========================================
import { ref, onMounted } from 'vue'
import { DollarSign, BarChart3, Users, Calendar, TrendingUp, Download } from 'lucide-vue-next'
import api from '@/services/axios'

// ========================================
// DADOS REATIVOS
// ========================================
// Estatísticas principais do relatório
const stats = ref({
  totalRevenue: 0,           // Faturamento total atual
  revenueGrowth: 0,          // Crescimento do faturamento (%)
  commissionsPaid: 0,        // Comissões pagas no período
  commissionsGrowth: 0,      // Crescimento das comissões (%)
  activeAffiliates: 0,       // Número de afiliados ativos
  affiliatesGrowth: 0,       // Crescimento de afiliados (%)
  newRegistrations: 0,       // Novos cadastros no período
  registrationsGrowth: 0     // Crescimento de cadastros (%)
})

// Dados das tabelas
const monthlyPerformance = ref([])  // Desempenho dos últimos 4 meses
const topAffiliates = ref([])       // Top 4 afiliados por performance
const loading = ref(true)           // Estado de carregamento

// ========================================
// FUNÇÕES UTILITÁRIAS
// ========================================

/**
 * Formata valores monetários para o padrão brasileiro
 * @param {number} value - Valor a ser formatado
 * @returns {string} Valor formatado (ex: "1.234,56")
 */
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

/**
 * Determina a classe CSS do badge baseada no nível de carreira
 * @param {string} level - Nível de carreira (Bronze, Prata, Ouro, Diamante)
 * @returns {string} Classes CSS para o badge
 */
const getLevelBadgeClass = (level) => {
  const levelLower = level.toLowerCase()
  if (levelLower.includes('diamante')) return 'bg-blue-100 text-blue-800'
  if (levelLower.includes('ouro')) return 'bg-yellow-100 text-yellow-800'
  if (levelLower.includes('prata')) return 'bg-gray-100 text-gray-800'
  if (levelLower.includes('bronze')) return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

/**
 * Função para exportar o relatório (PDF, Excel, etc.)
 * TODO: Implementar funcionalidade de exportação
 */
const exportReport = () => {
  // Implementar exportação (PDF, Excel, etc.)
  alert('Funcionalidade de exportação será implementada em breve!')
}

// ========================================
// FUNÇÕES PRINCIPAIS
// ========================================

/**
 * Carrega os dados do relatório geral da API
 * Em caso de erro, usa dados mockados para demonstração
 */
const loadReportData = async () => {
  try {
    loading.value = true
    
    // Buscar dados da API
    const response = await api.get('/api/core/general-report/')
    const data = response.data
    
    // Atualizar dados reativos
    stats.value = data.stats
    monthlyPerformance.value = data.monthly_performance
    topAffiliates.value = data.top_affiliates
    
  } catch (error) {
    console.error('Erro ao carregar dados do relatório:', error)
    
    // Fallback: dados mockados para demonstração
    stats.value = {
      totalRevenue: 125430.50,
      revenueGrowth: 15.2,
      commissionsPaid: 35240.75,
      commissionsGrowth: 8.5,
      activeAffiliates: 847,
      affiliatesGrowth: 12.1,
      newRegistrations: 156,
      registrationsGrowth: 25.3
    }
    
    // Dados mockados para desempenho mensal
    monthlyPerformance.value = [
      { month: 'Janeiro', revenue: 45230.50, commissions: 12450.75, affiliates: 234 },
      { month: 'Fevereiro', revenue: 52340.25, commissions: 14230.50, affiliates: 267 },
      { month: 'Março', revenue: 48560.75, commissions: 13560.25, affiliates: 289 },
      { month: 'Abril', revenue: 55430.50, commissions: 15240.75, affiliates: 312 }
    ]
    
    // Dados mockados para top afiliados
    topAffiliates.value = [
      { name: 'João Silva', sales: 25, commission: 5430.50, level: 'Diamante' },
      { name: 'Maria Santos', sales: 22, commission: 4850.25, level: 'Ouro' },
      { name: 'Pedro Costa', sales: 18, commission: 3920.75, level: 'Prata' },
      { name: 'Ana Oliveira', sales: 15, commission: 3240.50, level: 'Bronze' }
    ]
  } finally {
    loading.value = false
  }
}

// ========================================
// LIFECYCLE HOOKS
// ========================================
// Carregar dados quando o componente for montado
onMounted(() => {
  loadReportData()
})
</script>
