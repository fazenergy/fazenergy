<template>
  <div class="space-y-3">
    <!-- Toolbar de seleção de visualização -->
    <div class="bg-white border rounded p-3 flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
      <div class="flex items-center gap-2 flex-wrap">
        <label class="text-sm font-medium">Visualização:</label>
        <select v-model="view" class="border rounded px-3 py-2 text-sm min-w-[12rem]">
          <option value="genealogy">Árvore Genealógica</option>
          <option value="treeview">Treeview Vertical (com contagens)</option>
          <option value="grid">Estilo Grid</option>
        </select>
      </div>
      <div class="flex-1"></div>
      <div class="flex items-center gap-2">
        <input v-model.trim="search" type="text" placeholder="Pesquisar usuário..." class="border rounded px-3 py-2 text-sm md:w-80" />
        <button @click="search=''; fetchTree()" class="px-3 py-2 text-sm border rounded hover:bg-gray-50">Limpar</button>
      </div>
    </div>

    <div class="bg-white border rounded p-3 min-h-[400px]">
      <!-- VIEW 1: Árvore Genealógica (simples) -->
      <div v-if="view==='genealogy'">
        <div class="flex justify-center">
          <GenealogyNode :node="root" />
        </div>
      </div>

      <!-- VIEW 2: Treeview vertical com contagens -->
      <div v-else-if="view==='treeview'" class="overflow-auto">
        <ul class="tree">
          <TreeNode :node="root" />
        </ul>
      </div>

      <!-- VIEW 3: Grid -->
      <div v-else>
        <DataTable :columns="columns" :rows="flatRows" :loading="loading" :min-height="'400px'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/ui/DataTable.vue'
import api from '@/services/axios'
import GenealogyNode from '@/components/network/GenealogyNode.vue'
import TreeNode from '@/components/network/TreeNode.vue'
import { useAuthStore } from '@/store/auth'

const view = ref('genealogy')
const search = ref('')
const loading = ref(false)
const root = ref({ id: null, user: { username: '' }, level: 0, children: [] })
const auth = useAuthStore()

async function fetchTree() {
  try {
    loading.value = true
    const { data } = await api.get('/api/network/tree/')
    if (data?.root) {
      root.value = data.root
    } else {
      root.value = { id: null, user: { username: auth.user?.username || 'faz.raiz' }, level: 0, children: [] }
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchTree)

const flatRows = computed(() => (root.value.children || []).map(c => ({
  user: c.user?.username,
  city: c.city,
  plan: c.plan
})))

const columns = [
  { key: 'user', label: 'Usuário' },
  { key: 'city', label: 'Cidade' },
  { key: 'plan', label: 'Plano' },
]
</script>

<style scoped>
.tree { padding-left: 0; }
</style>

