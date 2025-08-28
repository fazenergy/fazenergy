<template>
  <main class="p-6 space-y-6">
    <div v-if="isLicensed && docsPending" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
      <div class="flex items-start gap-3">
        <div class="mt-0.5 w-2 h-2 rounded-full bg-amber-500"></div>
        <div>
          <div class="font-semibold text-amber-800">Você ainda não enviou seus documentos de licenciado para validação</div>
          <div class="text-amber-800/80 text-sm">Envie os documentos abaixo para prosseguir com a validação.</div>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold">Documentos do Licenciado</h1>
      <div v-if="isLicensed" class="text-sm text-gray-600">Status geral: <span :class="statusPillClass(generalStatus)">{{ labelStatus(generalStatus) }}</span></div>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full border">
        <thead class="bg-blue-600 text-white">
          <tr>
            <th class="px-3 py-2 text-left text-sm font-semibold">Tipo</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Observação</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Arquivo</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Status</th>
            <th class="px-3 py-2 text-right text-sm font-semibold">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.key" class="border-b last:border-b-0">
            <td class="px-3 py-2 text-sm">{{ labelType(row.key) }}</td>
            <td class="px-3 py-2 text-sm">
              <div v-if="row.doc">{{ row.doc.observation || '-' }}</div>
              <div v-else class="text-gray-400">-</div>
            </td>
            <td class="px-3 py-2 text-sm">
              <div v-if="row.doc?.file" class="flex items-center gap-2">
                <button @click="openPreview(row.doc.file)" class="text-blue-600 hover:underline">Ver anexo</button>
                <a :href="row.doc.file" download class="px-2 py-1 rounded bg-gray-200 text-gray-700 text-xs hover:bg-gray-300">Download</a>
              </div>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-3 py-2 text-sm">
              <span :class="statusPillClass(row.doc ? row.doc.stt_validate : 'missing')">
                {{ labelStatus(row.doc ? row.doc.stt_validate : 'missing') }}
              </span>
            </td>
            <td class="px-3 py-2 text-sm text-right space-x-2">
              <!-- Ações para Licenciado -->
              <template v-if="isLicensed">
                <button class="px-3 py-1.5 rounded bg-blue-600 text-white text-sm" @click="openUpload(row.key, row.doc)">{{ row.doc ? 'Reenviar' : 'Anexar' }}</button>
              </template>
              <!-- Ações para Operador -->
              <template v-else-if="isOperator && row.doc">
                <button class="px-3 py-1.5 rounded bg-emerald-600 text-white text-sm" @click="setStatus(row.doc, 'approved')">Aprovar</button>
                <button class="px-3 py-1.5 rounded bg-red-600 text-white text-sm" @click="openReject(row.doc)">Reprovar</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Upload/Reenvio -->
    <Modal v-model="showUpload" :header-blue="true" :no-header-border="true">
      <template #title>{{ currentDoc ? 'Editar Documento' : 'Enviar Documento' }}</template>
      <div class="space-y-4">
        <div v-if="formError" class="p-3 rounded border border-red-200 bg-red-50 text-sm text-red-700">{{ formError }}</div>
        <div>
          <label class="block text-sm font-medium">Tipo</label>
          <input type="text" class="w-full border rounded px-3 py-2 text-sm bg-gray-100" :value="labelType(currentType)" disabled />
        </div>
        <div>
          <label class="block text-sm font-medium">Arquivo</label>
          <input ref="fileInput" type="file" class="w-full border rounded px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium">Observação</label>
          <textarea v-model.trim="form.observation" rows="3" class="w-full border rounded px-3 py-2 text-sm"></textarea>
        </div>
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 rounded bg-gray-200 text-sm" @click="showUpload=false">Fechar</button>
          <button class="px-3 py-1.5 rounded bg-blue-600 text-white text-sm" @click="submitUpload">Gravar</button>
        </div>
      </div>
    </Modal>

    <!-- Modal Reprovar -->
    <Modal v-model="showReject" :header-blue="true" :no-header-border="true">
      <template #title>Reprovar Documento</template>
      <div class="space-y-4">
        <div class="text-sm">Informe o motivo da reprovação.</div>
        <textarea v-model.trim="rejectReason" rows="4" class="w-full border rounded px-3 py-2 text-sm"></textarea>
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 rounded bg-gray-200 text-sm" @click="showReject=false">Fechar</button>
          <button class="px-3 py-1.5 rounded bg-red-600 text-white text-sm" @click="confirmReject">Reprovar</button>
        </div>
      </div>
    </Modal>
    
    <!-- Modal de Visualização do Anexo -->
    <Modal v-model="showPreview" :header-blue="true" :no-header-border="true">
      <template #title>Visualizar Anexo</template>
      <div class="space-y-3">
        <div v-if="isImage(previewUrl)" class="max-h-[70vh] overflow-auto">
          <img :src="previewUrl" class="max-w-full h-auto" />
        </div>
        <div v-else-if="isPdf(previewUrl)" class="h-[70vh]">
          <iframe :src="previewUrl" class="w-full h-full" />
        </div>
        <div v-else class="text-sm text-gray-700">
          Visualização não suportada. Clique em baixar para abrir o arquivo.
          <div class="mt-3">
            <a :href="previewUrl" download class="px-3 py-1.5 rounded bg-gray-200 text-gray-800 text-sm hover:bg-gray-300">Baixar</a>
          </div>
        </div>
      </div>
    </Modal>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'

const auth = useAuthStore()
const isLicensed = computed(() => auth.user?.groups?.includes('Licenciado'))
const isOperator = computed(() => auth.user?.is_superuser || auth.user?.is_staff || auth.user?.groups?.includes('Operador'))

const DOC_TYPES = [
  { key: 'cpf', label: 'CPF' },
  { key: 'rg', label: 'RG' },
  { key: 'comprovante_endereco', label: 'Comprovante de Endereço' },
  { key: 'pis', label: 'PIS' }
]

const rows = ref([])
const generalStatus = ref('pending')
const docsPending = computed(() => generalStatus.value === 'pending')

async function fetchData() {
  const { data: docs } = await api.get('/api/core/licensed-documents/')
  const { data: dash } = await api.get('/api/core/dashboard/')
  generalStatus.value = dash?.documents?.status || 'pending'
  const byType = {}
  for (const d of docs || []) {
    byType[d.document_type] = d
  }
  rows.value = DOC_TYPES.map(t => ({ key: t.key, doc: byType[t.key] || null }))
}

onMounted(fetchData)

function labelType(key) {
  return DOC_TYPES.find(d => d.key === key)?.label || key
}
function labelStatus(st) {
  return ({
    missing: 'Pendente',
    pending: 'Aguardando aprovação',
    approved: 'Aprovado',
    rejected: 'Reprovado'
  })[st] || 'Pendente'
}
function statusPillClass(st) {
  const base = 'inline-flex items-center px-2 py-0.5 rounded text-xs '
  const map = {
    missing: base + 'bg-amber-100 text-amber-800',         // Pendente (amarelo)
    pending: base + 'bg-blue-100 text-blue-700',           // Aguardando aprovação (azul)
    approved: base + 'bg-emerald-100 text-emerald-800',    // Aprovado (verde)
    rejected: base + 'bg-red-100 text-red-800'             // Reprovado (vermelho)
  }
  return map[st] || map.missing
}
function openPreview(url) { previewUrl.value = url; showPreview.value = true }
function isPdf(url) { return /\.pdf($|\?)/i.test(url || '') }
function isImage(url) { return /\.(png|jpe?g|gif|webp|bmp|svg)($|\?)/i.test(url || '') }

const showUpload = ref(false)
const currentType = ref(null)
const currentDoc = ref(null)
const form = ref({ observation: '' })
const formError = ref('')
const fileInput = ref(null)
const showPreview = ref(false)
const previewUrl = ref('')

function openUpload(type, doc) {
  currentType.value = type
  currentDoc.value = doc || null
  form.value = { observation: doc?.observation || '' }
  showUpload.value = true
}

async function submitUpload() {
  const fd = new FormData()
  fd.append('document_type', currentType.value)
  if (fileInput.value?.files?.[0]) fd.append('file', fileInput.value.files[0])
  fd.append('observation', form.value.observation || '')
  try {
    if (currentDoc.value) {
      await api.patch(`/api/core/licensed-documents/${currentDoc.value.id}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    } else {
      await api.post('/api/core/licensed-documents/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    }
    showUpload.value = false
    await fetchData()
    alert('Documento enviado com sucesso!')
  } catch (e) {
    const data = e?.response?.data
    formError.value = typeof data === 'string' ? data : (data?.detail || Object.entries(data||{}).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(', '):v}`).join(' | ') || 'Erro ao enviar documento')
  }
}

const showReject = ref(false)
const rejectDoc = ref(null)
const rejectReason = ref('')

function openReject(doc) {
  rejectDoc.value = doc
  rejectReason.value = doc?.rejection_reason || ''
  showReject.value = true
}

async function confirmReject() {
  try {
    await api.patch(`/api/core/licensed-documents/${rejectDoc.value.id}/`, {
      stt_validate: 'rejected',
      rejection_reason: rejectReason.value || 'Documento inconsistente'
    })
    showReject.value = false
    await fetchData()
  } catch (e) {
    alert('Erro ao reprovar')
  }
}
</script>


