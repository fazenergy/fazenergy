<template>
  <div class="px-4 pt-2 pb-2 flex flex-col gap-3 min-h-[calc(100vh-100px)]">
    <!-- Toolbar padrão -->
    <div class="flex flex-wrap items-center gap-2 mb-2">
      <button @click="openModal()" class="h-8 px-3 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-1">
        <Plus class="w-4 h-4" /> Adicionar
      </button>
      <button @click="exportXls" class="h-8 px-3 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white flex items-center gap-1">
        <FileDown class="w-4 h-4" /> Exportar
      </button>
      <button @click="printList" class="h-8 px-3 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1">
        <Printer class="w-4 h-4" /> Imprimir
      </button>

      <div class="flex items-center gap-2 ml-auto min-w-[12rem] flex-1">
        <input v-model="searchText" type="text" placeholder="Pesquisar..." class="flex-1 h-8 border rounded px-2 text-sm" />
        <button @click="fetchCompanies" class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 hover:bg-blue-700 text-white" title="Pesquisar">
          <Search class="w-4 h-4" />
        </button>
        <button @click="clearFilters" class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 text-gray-700" title="Limpar">
          <Eraser class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Grid -->
    <DataTable :columns="columns" :rows="rows" :loading="loading">
      <template #title>Minhas Empresas</template>
      <template #col:actions="{ row }">
        <div class="text-right">
          <button class="px-2 py-1 text-xs rounded border text-blue-600 border-blue-600" @click="openModal(row)">Editar</button>
        </div>
      </template>
      <template #col:id="{ row }">#{{ row.id }}</template>
      <template #col:id_last="{ row }">#{{ row.id_last }}</template>
    </DataTable>

    <!-- Modal -->
    <Modal v-model="modalOpen" :header-blue="true" :no-header-border="true" max-width="max-w-6xl">
      <template #title>Empresa (PJ)</template>
        <!-- Tabs -->
        <div class="border-b mb-3 flex items-center gap-4">
          <button @click="tab='dados'" :class="tabBtnClass('dados')">Dados</button>
          <button @click="tab='endereco'" :class="tabBtnClass('endereco')">Endereço</button>
        </div>

        <div class="min-h-[55vh]">
        <!-- Tab: Dados -->
        <div v-if="tab==='dados'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <FormField label="CNPJ">
            <Input v-model="form.cnpj" placeholder="00.000.000/0000-00" mask="##.###.###/####-##" />
          </FormField>
          <FormField label="Razão Social">
            <Input v-model="form.razao_social" />
          </FormField>

          <FormField label="Nome Fantasia">
            <Input v-model="form.nome_fantasia" />
          </FormField>
          <FormField label="Telefone">
            <Input v-model="form.telefone" placeholder="(00) 00000-0000" mask="(##) #####-####" />
          </FormField>

          <FormField label="Inscrição Estadual">
            <Input v-model="form.insc_estadual" />
          </FormField>
          <FormField label="Inscrição Municipal">
            <Input v-model="form.insc_municipal" />
          </FormField>
        </div>

        <!-- Tab: Endereço -->
        <div v-if="tab==='endereco'" class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <FormField label="CEP">
            <Input v-model="form.cep" placeholder="00000-000" mask="#####-###" @blur="onCepBlur" />
          </FormField>
          <FormField label="Estado (UF)">
            <Select v-model="uf">
              <option value="">Selecione</option>
              <option v-for="s in ufs" :key="s" :value="s">{{ s }}</option>
            </Select>
          </FormField>
          <FormField label="Cidade">
            <Select v-model="form.city_id">
              <option value="">Selecione</option>
              <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
            </Select>
          </FormField>

          <FormField label="Endereço" class="md:col-span-2">
            <Input v-model="form.endereco" />
          </FormField>
          <FormField label="Número">
            <Input v-model="form.numero" />
          </FormField>

          <FormField label="Bairro">
            <Input v-model="form.bairro" />
          </FormField>
          <FormField label="Complemento" class="md:col-span-2">
            <Input v-model="form.complemento" />
          </FormField>

          <FormField label="Observação" class="md:col-span-3">
            <Textarea v-model="form.observacao" rows="3" />
          </FormField>
        </div>

        <div v-if="tab==='dados'" class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
          <div class="p-3 border rounded">
            <div class="font-semibold text-sm mb-2">Cartão CNPJ</div>
            <input type="file" @change="onFileChange($event, 'cnpj_card')" />
          </div>
          <div class="p-3 border rounded">
            <div class="font-semibold text-sm mb-2">Contrato Social</div>
            <input type="file" @change="onFileChange($event, 'social_contract')" />
          </div>
          <div class="md:col-span-2"><div v-if="docStatusText" class="mt-2 text-xs">Status: <span class="font-medium">{{ docStatusText }}</span></div></div>
        </div>
        </div>
      <template #footer>
        <div class="flex justify-end gap-2">
          <button @click="modalOpen=false" class="px-3 h-9 rounded border">Fechar</button>
          <button @click="saveCompany" :disabled="saving" class="px-3 h-9 rounded bg-emerald-600 hover:bg-emerald-700 text-white">Gravar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, FileDown, Printer, Search, Eraser } from 'lucide-vue-next'
import api from '@/services/axios'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import FormField from '@/components/ui/FormField.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Select from '@/components/ui/Select.vue'
import apiSvc from '@/services/axios'

const loading = ref(false)
const rows = ref([])
const searchText = ref('')

const columns = [
  { key: 'actions', label: 'Ações' },
  { key: 'id', label: 'ID' },
  { key: 'cnpj', label: 'CNPJ' },
  { key: 'razao_social', label: 'Razão Social' },
  { key: 'stt_validate', label: 'Status' },
  { key: 'id_last', label: 'ID' },
]

async function fetchCompanies(){
  loading.value = true
  try{
    const res = await api.get('/api/core/licensed-companies/', { params: { search: searchText.value || undefined } })
    rows.value = (res.data || []).map(x => ({ ...x, id_last: x.id }))
  }finally{
    loading.value = false
  }
}

function exportXls(){ window.print() }
function printList(){ window.print() }
function clearFilters(){ searchText.value=''; fetchCompanies() }

const modalOpen = ref(false)
const saving = ref(false)
const form = ref({ id:null, cnpj:'', razao_social:'', nome_fantasia:'', insc_estadual:'', insc_municipal:'', cep:'', endereco:'', numero:'', complemento:'', bairro:'', telefone:'', observacao:'', city_id:'' })
const pendingUploads = ref({})
const docStatusText = computed(() => (form.value.stt_validate || 'pending'))

// Estados e cidades (via ViaCEP + backend cities)
const uf = ref('')
const ufs = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
const cities = ref([])

async function onCepBlur(){
  const cep = (form.value.cep || '').replace(/\D/g, '')
  if(cep.length !== 8) return
  try{
    const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`)
    const data = await res.json()
    if(!data.erro){
      form.value.endereco = data.logradouro || form.value.endereco
      form.value.bairro = data.bairro || form.value.bairro
      uf.value = data.uf || uf.value
      await loadCitiesByUf()
      // Tenta selecionar cidade pelo nome
      const found = cities.value.find(c => (c.name || '').toLowerCase() === (data.localidade || '').toLowerCase())
      if(found) form.value.city_id = found.id
    }
  }catch{}
}

async function loadCitiesByUf(){
  if(!uf.value) { cities.value = []; return }
  try{
    const { data } = await apiSvc.get('/api/location/cities/', { params: { uf: uf.value } })
    cities.value = data || []
  }catch{ cities.value = [] }
}

function openModal(row){
  if(row){ form.value = { ...row }; pendingUploads.value = {} } else { form.value = { id:null, cnpj:'', razao_social:'', nome_fantasia:'', insc_estadual:'', insc_municipal:'', cep:'', endereco:'', numero:'', complemento:'', bairro:'', telefone:'', observacao:'' }; pendingUploads.value = {} }
  modalOpen.value = true
}

function onFileChange(e, type){
  const file = e.target.files?.[0]
  if(file){ pendingUploads.value[type] = file }
}

async function saveCompany(){
  saving.value = true
  try{
    const payload = { ...form.value }
    let res
    if(payload.id){ res = await api.put(`/api/core/licensed-companies/${payload.id}/`, payload) }
    else { res = await api.post('/api/core/licensed-companies/', payload) }
    const companyId = res.data.id
    // Upload de docs se houver
    for(const [docType, file] of Object.entries(pendingUploads.value)){
      const fd = new FormData()
      fd.append('owner_type', 'pj')
      fd.append('company', companyId)
      fd.append('document_type', docType)
      fd.append('file', file)
      await api.post('/api/core/licensed-documents/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    }
    modalOpen.value = false
    await fetchCompanies()
  }finally{
    saving.value = false
  }
}

onMounted(fetchCompanies)

// Tabs
const tab = ref('dados')
function tabBtnClass(k){
  return [
    'px-3 py-1.5 text-xs rounded',
    tab.value===k 
      ? 'bg-emerald-600 text-white' 
      : 'bg-white text-gray-700 hover:bg-emerald-50 border border-transparent'
  ]
}
</script>

<style scoped>
</style>

