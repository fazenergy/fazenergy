<template>
  <main class="p-6 space-y-6">
    <!-- Toolbar padrão (Exportar, Imprimir, Pesquisar) -->
    <div class="mb-3 bg-white border rounded p-3 flex flex-col md:flex-row md:items-center gap-3 md:gap-4">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm">Exportar XLS</button>
        <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm">Imprimir / PDF</button>
        <!-- Botão de cadastrar visível apenas para SUPERADMIN -->
        <button v-if="isSuperadmin" @click="showNew = true" class="px-2 py-1 h-8 text-xs rounded bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm">Cadastrar Licenciado</button>
      </div>
      <div class="flex items-center gap-2 flex-1">
        <input v-model.trim="q" type="text" placeholder="Pesquisar..." class="w-full md:w-80 border rounded px-2 py-1 h-8 text-xs" />
        <button @click="applySearch" class="px-2 py-1 h-8 text-xs rounded bg-gray-700 hover:bg-gray-800 text-white shadow-sm">Pesquisar</button>
        <button @click="clearSearch" class="px-2 py-1 h-8 text-xs border rounded hover:bg-gray-50">Limpar</button>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full border">
        <thead class="bg-blue-600 text-white">
          <tr>
            <th class="px-3 py-2 text-left text-sm font-semibold">Ações</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">ID</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Avatar</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Nome</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Login</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Qualificação</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Dtt Cadastro</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Cidade-UF</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Plano</th>
            <th class="px-3 py-2 text-right text-sm font-semibold">ID</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lic in filtered" :key="lic.id" class="border-b last:border-b-0">
            <td class="px-3 py-2 text-sm text-right space-x-1">
              <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 text-gray-700" @click="openReport(lic)" title="Relatório">
                <FileText class="w-4 h-4" />
              </button>
              <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 text-white" @click="openEdit(lic)" title="Editar">
                <Pencil class="w-4 h-4" />
              </button>
              <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-red-600 text-white" @click="resetPass(lic)" title="Resetar senha">
                <KeyRound class="w-4 h-4" />
              </button>
            </td>
            <td class="px-3 py-2 text-sm">{{ lic.id }}</td>
            <td class="px-3 py-2 text-sm">
              <img v-if="lic.user?.image_profile" :src="lic.user.image_profile" class="w-8 h-8 rounded-full object-cover" />
              <div v-else class="w-8 h-8 rounded-full bg-gray-200"></div>
            </td>
            <td class="px-3 py-2 text-sm">{{ (lic.user?.first_name || '') + ' ' + (lic.user?.last_name || '') }}</td>
            <td class="px-3 py-2 text-sm">{{ lic.user?.username }}</td>
            <td class="px-3 py-2 text-sm">{{ lic.current_career?.stage_name || '-' }}</td>
            <td class="px-3 py-2 text-sm">{{ formatDate(lic.dtt_record) }}</td>
            <td class="px-3 py-2 text-sm">{{ (lic.city_lookup?.name || '-') + (lic.city_lookup?.state ? ('-' + (lic.city_lookup.state.uf||'')) : '') }}</td>
            <td class="px-3 py-2 text-sm">{{ lic.plan?.name || '-' }}</td>
            <td class="px-3 py-2 text-sm text-right">{{ lic.id }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Relatório -->
    <Modal v-model="showReport" :header-blue="true" :no-header-border="true">
      <template #title>Relatório do Licenciado</template>
      <div v-if="current">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div><b>Nome Completo:</b> {{ fullName(current) }}</div>
          <div><b>Login:</b> {{ current.user?.username }}</div>
          <div><b>Indicador Original:</b> {{ current.original_indicator?.user?.username || '-' }}</div>
          <div><b>Plano atual:</b> {{ current.plan?.name || '-' }}</div>
          <div><b>Está ativo?</b> {{ current.stt_record ? 'Sim' : 'Não' }}</div>
          <div><b>Data de ativação:</b> {{ formatDate(current.dtt_activation) }}</div>
          <div><b>Diretos efetivados:</b> {{ current.stats?.directs_confirmed || 0 }}</div>
          <div><b>Diretos pré-cadastrados:</b> {{ current.stats?.directs_preregistered || 0 }}</div>
          <div><b>Compras realizadas:</b> {{ current.stats?.self_purchases || 0 }}</div>
          <div><b>Saldo conta virtual:</b> R$ {{ (current.virtual_account?.balance_available || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
          <div><b>Status documentação PF:</b> {{ docLabel(current.stt_document) }}</div>
        </div>
      </div>
    </Modal>

    <!-- Modal Edição (campos restritos) -->
    <Modal v-model="showEdit" :header-blue="true" :no-header-border="true">
      <template #title>Editar Licenciado</template>
      <div v-if="form">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div>
            <label class="text-xs text-gray-600">Nome</label>
            <input v-model="form.first_name" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-600">Sobrenome</label>
            <input v-model="form.last_name" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-600">Email</label>
            <input v-model="form.email" type="email" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-600">Senha (opcional)</label>
            <input v-model="form.password" type="password" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-600">CPF</label>
            <input v-model="form.cpf_cnpj" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-600">CEP</label>
            <input v-model="form.cep" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Endereço</label>
            <input v-model="form.address" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-600">Foto</label>
            <input ref="photo" type="file" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-4">
          <button class="px-3 py-1.5 rounded bg-gray-200 text-sm" @click="showEdit=false">Fechar</button>
          <button class="px-3 py-1.5 rounded bg-blue-600 text-white text-sm" @click="saveEdit">Gravar</button>
        </div>
      </div>
    </Modal>
    <!-- Modal Cadastro (aproveita o formulário existente do pré-cadastro) -->
    <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
      <template #title>Novo Licenciado</template>
      <FormPreRegister :in-modal="true" @close="showNew=false" />
      <template #footer>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 rounded border" @click="showNew=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white" @click="submitPreForm">Gravar</button>
        </div>
      </template>
    </Modal>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'
import { FileText, Pencil, KeyRound } from 'lucide-vue-next'
import FormPreRegister from '@/components/FormPreRegister.vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const list = ref([])
const q = ref('')
const filtered = computed(() => {
  const term = (q.value || '').toLowerCase()
  return list.value.filter(lic => !term || (lic.user?.username||'').toLowerCase().includes(term) || ((lic.user?.first_name||'') + ' ' + (lic.user?.last_name||'')).toLowerCase().includes(term))
})

const showReport = ref(false)
const current = ref(null)
const showEdit = ref(false)
const form = ref(null)
const photo = ref(null)
const showNew = ref(false)
const isSuperadmin = computed(() => auth.user?.is_superuser || auth.user?.groups?.includes('Superadmin'))

function submitPreForm() {
  try {
    const formEl = document.getElementById('preRegisterForm')
    if (formEl && typeof formEl.requestSubmit === 'function') {
      formEl.requestSubmit()
    } else if (formEl) {
      formEl.submit()
    }
  } catch {}
}

function formatDate(dt) { try { return new Date(dt).toLocaleString('pt-BR') } catch { return '-' } }
function fullName(lic) { return (lic.user?.first_name||'') + ' ' + (lic.user?.last_name||'') }
function docLabel(st) { return ({ pending: 'Pendente', approved: 'Aprovado', rejected: 'Reprovado' })[st] || '-' }

async function fetchList() {
  const { data } = await api.get('/api/core/licensed/')
}

onMounted(async () => {
  // Lista de licenciados simples usando endpoint licensed do core
  try {
    const { data } = await api.get('/api/core/licensed/')
    // Se vier paginado, use results; caso contrário use data direto
    list.value = data?.results || data || []
  } catch (e) {
    list.value = []
  }
})

function openReport(lic) { current.value = lic; showReport.value = true }
function openEdit(lic) {
  current.value = lic
  form.value = {
    first_name: lic.user?.first_name || '',
    last_name: lic.user?.last_name || '',
    email: lic.user?.email || '',
    password: '',
    cpf_cnpj: lic.cpf_cnpj || '',
    cep: lic.cep || '',
    address: lic.address || ''
  }
  showEdit.value = true
}

async function saveEdit() {
  const fd = new FormData()
  fd.append('first_name', form.value.first_name)
  fd.append('last_name', form.value.last_name)
  fd.append('email', form.value.email)
  if (form.value.password) fd.append('password', form.value.password)
  fd.append('cpf_cnpj', form.value.cpf_cnpj)
  fd.append('cep', form.value.cep)
  fd.append('address', form.value.address)
  if (photo.value?.files?.[0]) fd.append('image_profile', photo.value.files[0])
  await api.patch('/api/core/profile/', fd)
  showEdit.value = false
}

async function resetPass(lic) {
  alert('Reset de senha enviado para: ' + (lic.user?.username || '-'))
}
</script>


