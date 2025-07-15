<!-- src/views/Dashboard.vue -->
<!-- src/views/Dashboard.vue -->
<template>
<div>
   <!-- ✅ Botão visível só para afiliados -->
    <button
      v-if="isAffiliate"
      @click="goToPreRegister"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    >
      Cadastrar Afiliado
    </button>
</div>
<div class="flex">
    <div class="flex-1">
    <main class="p-6 space-y-6">

    <!-- Cards principais -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg hover:scale-[1.01] transition-transform">
         <template #title><div>Total de Afiliados</div></template>
         <template #content><div><p class="text-2xl font-bold">R$ 1.234</p></div></template>
         <template #description><div>+20.1% em relação ao mês passado</div></template>
         <template #icon><UserPlus class="w-5 h-5" /></template>
      </Card>

      <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg hover:scale-[1.01] transition-transform">
         <template #title><div>Comissões Pagas</div></template>
         <template #content><div><p class="text-2xl font-bold">R$ 145.230,5</p></div></template>
         <template #description><div>+12.5% em relação ao mês passado</div></template>
         <template #icon><DollarSign class="w-5 h-5" /></template>
      </Card>

      <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-lg hover:scale-[1.01] transition-transform">
         <template #title><div>Usinas Vendidas Mês</div></template>
         <template #content><div><p class="text-2xl font-bold">573</p></div></template>
         <template #description><div>+8.2% em relação ao mês passado</div></template>
         <template #icon><TrendingUp class="w-5 h-5" /></template>
      </Card>

      <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-lg hover:scale-[1.01] transition-transform">
         <template #title><div>Afiliados Ativos</div></template>
         <template #content><div><p class="text-2xl font-bold">856</p></div></template>
         <template #description><div>+5.1% em relação ao mês passado</div></template>
         <template #icon><UserCheck class="w-5 h-5" /></template>
      </Card>
  </div>

  <!-- Ações rápidas, relatórios e configurações -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div class="border p-4 rounded">
            <h2 class="font-bold mb-2">Ações Rápidas</h2>
            <button class="block w-full p-2 bg-blue-500 text-white rounded mb-2">Gerenciar Afiliados</button>
            <button class="block w-full p-2 bg-purple-500 text-white rounded">Árvore da Rede</button>
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
import { computed } from 'vue'
import Card from '@/components/ui/Card.vue'
import { UserPlus, DollarSign, TrendingUp, UserCheck } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

// Exemplo: se você salva grupos no `auth.user`
const isAffiliate = computed(() => {
  return auth.user?.groups?.includes('Afiliado')
})

function goToPreRegister() {
  router.push('/preRegister')
}
</script>
