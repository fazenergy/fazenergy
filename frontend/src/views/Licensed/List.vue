<template>
  <div class="space-y-3">
    <!-- Toolbar compacta: botões + busca -->
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button v-if="isSuperadmin" @click="openNewModal" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <Plus class="w-4 h-4" />
          <span>Adicionar</span>
        </button>
        <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <FileDown class="w-4 h-4" />
          <span>Exportar</span>
        </button>
        <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <Printer class="w-4 h-4" />
          <span>Imprimir</span>
        </button>

        <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
          <input v-model.trim="q" type="text" placeholder="Pesquisar..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
          <button @click="applySearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 hover:bg-blue-700 text-white" title="Pesquisar">
            <Search class="w-4 h-4" />
          </button>
          <button @click="clearSearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 text-gray-700" title="Limpar">
            <Eraser class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div ref="gridWrapper">
      <DataTable :columns="columns" :rows="filtered" :loading="loading" :min-height="gridMinHeight">
        <template #title>Licenciados</template>
        <template #col:actions="{ row }">
          <div class="flex items-center gap-1">
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 text-gray-700" @click="openReport(row)" title="Relatório">
              <FileText class="w-4 h-4" />
            </button>
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 text-white" @click="openEdit(row)" title="Editar">
              <Pencil class="w-4 h-4" />
            </button>
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-red-600 text-white" @click="resetPass(row)" title="Resetar senha">
              <KeyRound class="w-4 h-4" />
            </button>
          </div>
        </template>
        <template #col:avatar="{ row }">
          <img v-if="row.user?.image_profile" :src="row.user.image_profile" class="w-8 h-8 rounded-full object-cover" />
          <div v-else class="w-8 h-8 rounded-full bg-gray-200"></div>
        </template>
        <template #col:name="{ row }">
          {{ fullNameOrUsername(row) }}
        </template>
        <template #col:login="{ row }">{{ row.user?.username }}</template>
        <template #col:career="{ row }">{{ row.current_career?.stage_name || 'nenhuma' }}</template>
        <template #col:created="{ row }">{{ formatDate(row.dtt_record) }}</template>
        <template #col:city="{ row }">{{ (row.city_lookup?.name || '-') + (row.city_lookup?.state ? ('-' + (row.city_lookup.state.uf||'')) : '') }}</template>
        <template #col:plan="{ row }">{{ row.plan?.name || '-' }}</template>
        <template #col:status="{ row }">{{ row.stt_record ? 'Ativo' : 'Inativo' }}</template>
      </DataTable>
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
        <div class="grid grid-cols-1 md:grid-cols-6 gap-4 text-sm">
          <!-- Foto à esquerda + botão Anexar abaixo -->
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Foto</label>
            <div class="mt-1 w-28 h-28 rounded-md bg-gray-100 border overflow-hidden flex items-center justify-center">
              <img v-if="current?.user?.image_profile || previewPhoto" :src="previewPhoto || current?.user?.image_profile" class="w-full h-full object-cover" />
            </div>
            <div class="mt-2">
              <button type="button" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm" @click="triggerPhoto">Anexar</button>
              <input ref="photo" type="file" class="hidden" @change="onPhotoChange" />
            </div>
          </div>
          <!-- Área de campos (direita) -->
          <div class="md:col-span-5 grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Nome / Sobrenome -->
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Nome</label>
              <input v-model="form.first_name" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Sobrenome</label>
              <input v-model="form.last_name" class="w-full border rounded px-3 py-2 text-sm" />
            </div>

            <!-- Email / Senha -->
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Email</label>
              <input v-model="form.email" type="email" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Senha (opcional)</label>
              <input v-model="form.password" type="password" class="w-full border rounded px-3 py-2 text-sm" />
            </div>

            <!-- Doc / CEP / Estado / Cidade -->
            <div class="md:col-span-1">
              <label class="text-xs text-gray-600">CPF</label>
              <input v-model="form.cpf_cnpj" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-1">
              <label class="text-xs text-gray-600">CEP</label>
              <input v-model="form.cep" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-1">
              <label class="text-xs text-gray-600">Estado</label>
              <select v-model="form.state_id" class="w-full border rounded px-3 py-2 text-sm">
                <option :value="null">Selecione</option>
                <option v-for="s in states" :key="s.id" :value="s.id">{{ s.uf }}</option>
              </select>
            </div>
            <div class="md:col-span-1">
              <label class="text-xs text-gray-600">Cidade</label>
              <select v-model="form.city_id" class="w-full border rounded px-3 py-2 text-sm">
                <option :value="null">Selecione</option>
                <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>

            <!-- Bairro / Endereço / Número -->
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Bairro</label>
              <input v-model="form.district" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Endereço</label>
              <input v-model="form.address" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-1">
              <label class="text-xs text-gray-600">Número</label>
              <input v-model="form.number" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
            <div class="md:col-span-3">
              <label class="text-xs text-gray-600">Complemento</label>
              <input v-model="form.complement" class="w-full border rounded px-3 py-2 text-sm" />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-2 mt-4">
          <button class="px-3 py-1.5 rounded bg-gray-200 text-sm" @click="showEdit=false">Fechar</button>
          <button class="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm" @click="saveEdit">Gravar</button>
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
          <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white" @click="submitPreForm">Gravar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'
import DataTable from '@/components/ui/DataTable.vue'
import { FileText, Pencil, KeyRound, Plus, FileDown, Printer, Search, Eraser } from 'lucide-vue-next'
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
const states = ref([])
const cities = ref([])
const previewPhoto = ref('')

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

function openNewModal() {
  showNew.value = true
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
  try {
    const { data: s } = await api.get('/api/location/states/')
    states.value = s || []
  } catch {}
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))

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
    address: lic.address || '',
    number: lic.number || '',
    complement: lic.complement || '',
    district: lic.district || '',
    state_id: lic.city_lookup?.state?.id || null,
    city_id: lic.city_lookup?.id || null
  }
  previewPhoto.value = ''
  if (form.value.state_id) loadCities(form.value.state_id)
  showEdit.value = true
}

function applySearch() {}

async function saveEdit() {
  const fd = new FormData()
  fd.append('first_name', form.value.first_name)
  fd.append('last_name', form.value.last_name)
  fd.append('email', form.value.email)
  if (form.value.password) fd.append('password', form.value.password)
  fd.append('cpf_cnpj', form.value.cpf_cnpj)
  fd.append('cep', form.value.cep)
  fd.append('address', form.value.address)
  fd.append('number', form.value.number)
  fd.append('complement', form.value.complement)
  fd.append('district', form.value.district)
  if (form.value.city_id) fd.append('city_lookup', form.value.city_id)
  if (photo.value?.files?.[0]) fd.append('image_profile', photo.value.files[0])
  await api.patch('/api/core/profile/', fd)
  showEdit.value = false
}

async function resetPass(lic) {
  alert('Reset de senha enviado para: ' + (lic.user?.username || '-'))
}

function onPhotoChange(e) {
  const f = e?.target?.files?.[0]
  if (!f) { previewPhoto.value = ''; return }
  const r = new FileReader()
  r.onload = () => { previewPhoto.value = r.result }
  r.readAsDataURL(f)
}

function triggerPhoto() {
  try { photo.value?.click() } catch {}
}

async function loadCities(stateId) {
  try {
    const { data } = await api.get('/api/location/cities/', { params: { state: stateId } })
    cities.value = data || []
  } catch { cities.value = [] }
}

watch(() => form.value?.state_id, (nv) => { if (nv) { form.value.city_id = null; loadCities(nv) } else { cities.value = []; form.value.city_id = null } })

// DataTable columns e altura dinâmica
const columns = [
  { key: 'actions', label: 'Ações' },
  { key: 'avatar', label: 'Avatar' },
  { key: 'name', label: 'Nome' },
  { key: 'login', label: 'Login' },
  { key: 'career', label: 'Qualificação' },
  { key: 'created', label: 'Dtt Cadastro' },
  { key: 'city', label: 'Cidade-UF' },
  { key: 'plan', label: 'Plano' },
  { key: 'status', label: 'Status' },
]

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}

function fullNameOrUsername(row) {
  const fn = row.user?.first_name || ''
  const ln = row.user?.last_name || ''
  const full = `${fn} ${ln}`.trim()
  return full || (row.user?.username || '-')
}
</script>


