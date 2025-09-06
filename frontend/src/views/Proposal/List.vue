<template>
  <div class="mb-3 bg-white rounded">
    <div class="flex items-center gap-2 flex-wrap">
      <button @click="openNewModal" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
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
        <input v-model.trim="search" type="text" placeholder="Pesquisar..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
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
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
      <template #title>Propostas</template>
      <template #col:id="{ row }">{{ row.id }}</template>
      <template #col:cliente="{ row }">{{ row.customer_name || row.customer?.name || '-' }}</template>
      <template #col:cidade="{ row }">{{ row.city_lookup?.name || row.city_name || '-' }}</template>
      <template #col:produto="{ row }">{{ row.product?.name || '-' }}</template>
      <template #col:status="{ row }">{{ row.status || '-' }}</template>
      <template #col:created="{ row }">{{ formatDate(row.dtt_record || row.created_at) }}</template>
    </DataTable>
  </div>

  <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
    <template #title>Nova Proposta</template>
    <div class="p-2 text-sm text-gray-800">
      <div class="grid grid-cols-1 md:grid-cols-6 gap-3">
        <div v-if="loadingProviders" class="md:col-span-6 text-blue-700 text-xs inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
          Buscando distribuidoras...
        </div>
        <div class="md:col-span-2">
          <label class="text-xs text-gray-600">ID do Licenciado</label>
          <input v-model.trim="form.licensed_id" type="number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Ex.: 4" />
        </div>
        <div class="md:col-span-2">
          <label class="text-xs text-gray-600">CEP Instalação</label>
          <input v-model.trim="form.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="Somente números" />
        </div>
        <div class="md:col-span-2">
          <label class="text-xs text-gray-600">Tipo de Imóvel</label>
          <select v-model="form.property_type" class="w-full border rounded px-2 py-1 text-sm">
            <option value="">Selecione</option>
            <option>Casa</option>
            <option>Apartamento</option>
            <option>Comercial</option>
            <option>Rural</option>
          </select>
        </div>

        <div class="md:col-span-2" v-if="validatedStep">
          <label class="text-xs text-gray-600">Proprietário do Imóvel</label>
          <select v-model="form.owner" class="w-full border rounded px-2 py-1 text-sm">
            <option value="">Selecione</option>
            <option>Próprio</option>
            <option>Outro</option>
          </select>
        </div>
        <div class="md:col-span-2" v-if="validatedStep">
          <label class="text-xs text-gray-600">Distribuidora</label>
          <select v-model="form.energy_provider_id" @change="onProviderChange" class="w-full border rounded px-2 py-1 text-sm">
            <option value="">Selecione</option>
            <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="md:col-span-2 flex items-end gap-2">
          <button type="button" @click="validateInitial" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs" :disabled="loadingProviders">
            {{ loadingProviders ? 'Validando...' : 'Validar e carregar distribuidora' }}
          </button>
        </div>

        <div class="md:col-span-2" v-if="validatedStep">
          <label class="text-xs text-gray-600">Unidade Consumidora</label>
          <input v-model.trim="form.consumer_unit" class="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div class="md:col-span-2" v-if="validatedStep">
          <label class="text-xs text-gray-600">Grupo de Consumo</label>
          <input v-model.trim="form.consumer_group" class="w-full border rounded px-2 py-1 text-sm" placeholder="Ex.: B1, A4" />
        </div>

        <div class="md:col-span-1">
          <label class="text-xs text-gray-600">Pessoa</label>
          <select v-model="form.contract_person" class="w-full border rounded px-2 py-1 text-sm">
            <option value="PF">PF</option>
            <option value="PJ">PJ</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <label class="text-xs text-gray-600">CPF/CNPJ</label>
          <input v-model.trim="form.fiscal_number" class="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div class="md:col-span-3" v-if="validatedStep">
          <label class="text-xs text-gray-600">E-mail do Vendedor</label>
          <input v-model.trim="form.seller_email" type="email" class="w-full border rounded px-2 py-1 text-sm" />
        </div>

        <div class="md:col-span-3" v-if="validatedStep">
          <label class="text-xs text-gray-600">Visita 1</label>
          <input v-model.trim="form.visit_1" type="datetime-local" class="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div class="md:col-span-3" v-if="validatedStep">
          <label class="text-xs text-gray-600">Visita 2</label>
          <input v-model.trim="form.visit_2" type="datetime-local" class="w-full border rounded px-2 py-1 text-sm" />
        </div>

        <!-- Consumo Mensal -->
        <div v-if="validatedStep" class="md:col-span-6 grid grid-cols-2 md:grid-cols-6 gap-3">
          <div class="md:col-span-6 font-semibold text-gray-700">Consumo Mensal (kWh)</div>
          <div v-for="m in months" :key="m.key">
            <label class="text-[10px] text-gray-600">{{ m.label }}</label>
            <input v-model.number="form.monthly_consumption[m.key]" type="number" min="0" class="w-full border rounded px-2 py-1 text-sm" />
          </div>
        </div>

        <!-- Atores -->
        <div v-if="validatedStep" class="md:col-span-6 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <div class="font-semibold text-gray-700 mb-1">Contratante</div>
            <div class="grid grid-cols-1 gap-2">
              <input v-model.trim="actors.contractor.legal_name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Razão Social (se PJ)" />
              <input v-model.trim="actors.contractor.name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Nome" />
              <input v-model.trim="actors.contractor.cellphone" class="w-full border rounded px-2 py-1 text-sm" placeholder="Celular" />
              <input v-model.trim="actors.contractor.email" type="email" class="w-full border rounded px-2 py-1 text-sm" placeholder="E-mail" />
              <input v-model.trim="actors.contractor.cpf" class="w-full border rounded px-2 py-1 text-sm" placeholder="CPF (se PF)" />
              <input v-model.trim="actors.contractor.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="CEP" />
              <input v-model.trim="actors.contractor.address" class="w-full border rounded px-2 py-1 text-sm" placeholder="Endereço" />
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.contractor.number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Número" />
                <input v-model.trim="actors.contractor.neighborhood" class="w-full border rounded px-2 py-1 text-sm" placeholder="Bairro" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.contractor.city" class="w-full border rounded px-2 py-1 text-sm" placeholder="Cidade" />
                <input v-model.trim="actors.contractor.st" class="w-full border rounded px-2 py-1 text-sm" placeholder="UF" />
              </div>
            </div>
          </div>

          <div>
            <div class="font-semibold text-gray-700 mb-1">Proprietário</div>
            <div class="grid grid-cols-1 gap-2">
              <input v-model.trim="actors.owner.name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Nome" />
              <input v-model.trim="actors.owner.cellphone" class="w-full border rounded px-2 py-1 text-sm" placeholder="Celular" />
              <input v-model.trim="actors.owner.email" type="email" class="w-full border rounded px-2 py-1 text-sm" placeholder="E-mail" />
              <input v-model.trim="actors.owner.cpf" class="w-full border rounded px-2 py-1 text-sm" placeholder="CPF" />
              <input v-model.trim="actors.owner.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="CEP" />
              <input v-model.trim="actors.owner.address" class="w-full border rounded px-2 py-1 text-sm" placeholder="Endereço" />
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.owner.number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Número" />
                <input v-model.trim="actors.owner.neighborhood" class="w-full border rounded px-2 py-1 text-sm" placeholder="Bairro" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.owner.city" class="w-full border rounded px-2 py-1 text-sm" placeholder="Cidade" />
                <input v-model.trim="actors.owner.st" class="w-full border rounded px-2 py-1 text-sm" placeholder="UF" />
              </div>
            </div>
          </div>

          <div>
            <div class="font-semibold text-gray-700 mb-1">Responsável Legal (PJ)</div>
            <div class="grid grid-cols-1 gap-2">
              <input v-model.trim="actors.legal_responsible.name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Nome" />
              <input v-model.trim="actors.legal_responsible.cellphone" class="w-full border rounded px-2 py-1 text-sm" placeholder="Celular" />
              <input v-model.trim="actors.legal_responsible.email" type="email" class="w-full border rounded px-2 py-1 text-sm" placeholder="E-mail" />
              <input v-model.trim="actors.legal_responsible.cpf" class="w-full border rounded px-2 py-1 text-sm" placeholder="CPF" />
              <input v-model.trim="actors.legal_responsible.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="CEP" />
              <input v-model.trim="actors.legal_responsible.address" class="w-full border rounded px-2 py-1 text-sm" placeholder="Endereço" />
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.legal_responsible.number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Número" />
                <input v-model.trim="actors.legal_responsible.neighborhood" class="w-full border rounded px-2 py-1 text-sm" placeholder="Bairro" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.legal_responsible.city" class="w-full border rounded px-2 py-1 text-sm" placeholder="Cidade" />
                <input v-model.trim="actors.legal_responsible.st" class="w-full border rounded px-2 py-1 text-sm" placeholder="UF" />
              </div>
            </div>
          </div>
        </div>

        <div v-if="errorMsg" class="md:col-span-6 text-red-600 text-xs">{{ errorMsg }}</div>
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button @click="showNew=false" class="px-4 py-2 rounded border">Fechar</button>
        <button @click="submitProposal" :disabled="saving" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">
          {{ saving ? 'Gravando...' : 'Gravar' }}
        </button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import api from '@/services/axios'
import { Plus, FileDown, Printer, Search, Eraser } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)
const search = ref('')
const auth = useAuthStore()

// Form state
const form = ref({
  licensed_id: '',
  zip_code: '',
  property_type: '',
  owner: '',
  energy_provider_id: '',
  energy_provider_name: '',
  consumer_unit: '',
  consumer_group: '',
  contract_person: 'PF',
  fiscal_number: '',
  seller_email: '',
  visit_1: '',
  visit_2: '',
  monthly_consumption: {
    january: 0, february: 0, march: 0, april: 0, may: 0, june: 0,
    july: 0, august: 0, september: 0, october: 0, november: 0, december: 0
  }
})
const months = [
  { key: 'january', label: 'Jan' }, { key: 'february', label: 'Fev' },
  { key: 'march', label: 'Mar' }, { key: 'april', label: 'Abr' },
  { key: 'may', label: 'Mai' }, { key: 'june', label: 'Jun' },
  { key: 'july', label: 'Jul' }, { key: 'august', label: 'Ago' },
  { key: 'september', label: 'Set' }, { key: 'october', label: 'Out' },
  { key: 'november', label: 'Nov' }, { key: 'december', label: 'Dez' }
]
const actors = ref({
  contractor: { actor: 'contractor', legal_name: '', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
  owner: { actor: 'owner', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
  legal_responsible: { actor: 'legal_responsible', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
})
const providers = ref([])
const loadingProviders = ref(false)
const saving = ref(false)
const errorMsg = ref('')
const validatedStep = ref(false)

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}

onMounted(async () => {
  try {
    loading.value = true
    const { data } = await api.get('/api/contractor/proposals/')
    rows.value = data
  } catch (e) {
    rows.value = []
  } finally {
    loading.value = false
  }
  // Prefill licensed_id se existir no perfil
  try {
    const prof = await auth.fetchProfile()
    if (prof?.licensed_id) {
      form.value.licensed_id = prof.licensed_id
    }
  } catch {}
})

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'cliente', label: 'Cliente' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'produto', label: 'Produto' },
  { key: 'status', label: 'Status' },
  { key: 'created', label: 'Cadastro' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [
      r.id,
      r.customer_name || r.customer?.name,
      r.city_lookup?.name || r.city_name,
      r.product?.name,
      r.status
    ].some(v => (v || '').toString().toLowerCase().includes(q))
    return matchSearch
  })
})

function applySearch() {}
function clearSearch() { search.value = '' }

function exportExcel() {
  const header = ['ID', 'Cliente', 'Cidade', 'Produto', 'Status', 'Cadastro']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.id || '')}</td>`+
    `<td>${(r.customer_name || r.customer?.name || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.product?.name || '')}</td>`+
    `<td>${(r.status || '')}</td>`+
    `<td>${formatDate(r.dtt_record || r.created_at) || ''}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `propostas_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.id || '')}</td>`+
    `<td>${(r.customer_name || r.customer?.name || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.product?.name || '')}</td>`+
    `<td>${(r.status || '')}</td>`+
    `<td>${formatDate(r.dtt_record || r.created_at) || ''}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Propostas</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Propostas</h3>
    <table>
      <thead><tr><th>ID</th><th>Cliente</th><th>Cidade</th><th>Produto</th><th>Status</th><th>Cadastro</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

const showNew = ref(false)
function openNewModal() { showNew.value = true }

async function validateInitial() {
  try {
    errorMsg.value = ''
    validatedStep.value = false
    const cep = (form.value.zip_code || '').replace(/\D/g, '')
    const cpf = (form.value.fiscal_number || '').replace(/\D/g, '')
    if (!form.value.licensed_id) throw new Error('Informe o ID do Licenciado')
    if (!cep) throw new Error('Informe o CEP de instalação')
    if (!cpf) throw new Error('Informe o CPF/CNPJ')
    if (!form.value.property_type) throw new Error('Informe o tipo de imóvel')

    // Verifica existência de proposta ativa
    const { data: ex } = await api.get('/api/contractor/proposals/exists/', { params: { zip_code: cep, cpf_cnpj: cpf } })
    if (ex?.exists) {
      throw new Error('Já existe proposta ativa para este CPF/CNPJ e CEP.')
    }

    // Busca distribuidora
    await fetchProviders()

    validatedStep.value = true
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e?.message || 'Falha na validação inicial'
  }
}

async function fetchProviders() {
  try {
    loadingProviders.value = true
    errorMsg.value = ''
    if (!form.value.zip_code) { errorMsg.value = 'Informe o CEP para buscar a distribuidora.'; return }
    const cep = (form.value.zip_code || '').replace(/\D/g, '')
    const ptype = encodeURIComponent(form.value.property_type || '')
    const url = ptype ? `/api/contractor/revo/cep/${cep}/${ptype}/` : `/api/contractor/revo/cep/${cep}/`
    const { data } = await api.get(url)
    providers.value = Array.isArray(data?.data) ? data.data : []
    if (providers.value.length) {
      form.value.energy_provider_id = providers.value[0].id
      form.value.energy_provider_name = providers.value[0].name
    }
  } catch (e) {
    providers.value = []
    errorMsg.value = 'Falha ao buscar distribuidoras para o CEP informado.'
  } finally {
    loadingProviders.value = false
  }
}

function onProviderChange() {
  const sel = providers.value.find(p => String(p.id) === String(form.value.energy_provider_id))
  form.value.energy_provider_name = sel?.name || ''
}

async function submitProposal() {
  try {
    saving.value = true
    errorMsg.value = ''

    // Validações mínimas
    if (!form.value.licensed_id) throw new Error('Informe o ID do Licenciado')
    if (!form.value.zip_code) throw new Error('Informe o CEP de instalação')
    if (!form.value.contract_person) throw new Error('Informe o tipo de pessoa (PF/PJ)')
    if (form.value.contract_person === 'PJ') {
      const lr = actors.value.legal_responsible
      if (!lr.name || !lr.cpf) throw new Error('Responsável legal é obrigatório para PJ (nome e CPF)')
    }

    const payload = {
      licensed_id: Number(form.value.licensed_id),
      zip_code: (form.value.zip_code || '').replace(/\D/g, ''),
      property_type: form.value.property_type || null,
      owner: form.value.owner || null,
      energy_provider_id: form.value.energy_provider_id ? Number(form.value.energy_provider_id) : null,
      energy_provider_name: form.value.energy_provider_name || null,
      consumer_unit: form.value.consumer_unit || null,
      consumer_group: form.value.consumer_group || null,
      contract_person: form.value.contract_person,
      fiscal_number: (form.value.fiscal_number || '').replace(/\D/g, ''),
      seller_email: form.value.seller_email || null,
      visit_1: form.value.visit_1 || null,
      visit_2: form.value.visit_2 || null,
      monthly_consumption: { ...form.value.monthly_consumption },
      lead_actors: [actors.value.contractor, actors.value.owner, actors.value.legal_responsible].filter(a => a && (a.name || a.legal_name))
    }

    const { data } = await api.post('/api/contractor/revo/simulation/', payload)
    // Atualiza a lista
    await refreshList()
    showNew.value = false
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e?.message || 'Erro ao salvar a proposta'
  } finally {
    saving.value = false
  }
}

async function refreshList() {
  try {
    loading.value = true
    const { data } = await api.get('/api/contractor/proposals/')
    rows.value = data
  } finally { loading.value = false }
}

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}
onMounted(() => {
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))
</script>


