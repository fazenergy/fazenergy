<template>
  <main class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold">Revisão de Documentos</h1>
    </div>

    <!-- Toolbar padrão -->
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
          <input v-model.trim="filters.licensed" placeholder="Usuário (username)" class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
          <select v-model="filters.status" class="border rounded px-2 py-1 h-8 text-xs">
            <option value="">Todos</option>
            <option value="pending">Aguardando aprovação</option>
            <option value="approved">Aprovado</option>
            <option value="rejected">Reprovado</option>
          </select>
          <button @click="applySearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 hover:bg-blue-700 text-white" title="Pesquisar">
            <Search class="w-4 h-4" />
          </button>
          <button @click="clearSearch" class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 text-gray-700" title="Limpar">
            <Eraser class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full border">
        <thead class="bg-blue-600 text-white">
          <tr>
            <th class="px-3 py-2 text-left text-sm font-semibold">ID</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Licenciado</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Tipo</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Observação</th>
            <th class="px-3 py-2 text-left text-sm font-semibold">Arquivo</th>
            <th class="px-3 py-2 text-right text-sm font-semibold">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in docs" :key="doc.id" class="border-b last:border-b-0">
            <td class="px-3 py-2 text-sm">{{ doc.id }}</td>
            <td class="px-3 py-2 text-sm">{{ doc.licensed_username }}</td>
            <td class="px-3 py-2 text-sm">{{ labelType(doc.document_type) }}</td>
            <td class="px-3 py-2 text-sm">{{ doc.observation || '-' }}</td>
            <td class="px-3 py-2 text-sm">
              <div v-if="doc.file" class="flex items-center gap-2">
                <button @click="openPreview(doc.file)" class="text-blue-600 hover:underline">Ver anexo</button>
                <a :href="doc.file" download class="px-2 py-1 rounded bg-gray-200 text-gray-700 text-xs hover:bg-gray-300">Download</a>
              </div>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-3 py-2 text-sm text-right space-x-2">
              <button class="px-3 py-1.5 rounded bg-emerald-600 text-white text-sm" @click="setStatus(doc, 'approved')">Aprovar</button>
              <button class="px-3 py-1.5 rounded bg-red-600 text-white text-sm" @click="openReject(doc)">Reprovar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model="showReject" :header-blue="true" :no-header-border="true">
      <template #title>Reprovar Documento</template>
      <div class="space-y-4">
        <div class="text-sm">Motivo da reprovação</div>
        <textarea v-model.trim="rejectReason" rows="4" class="w-full border rounded px-3 py-2 text-sm"></textarea>
        <div class="flex justify-end gap-2">
          <button class="px-3 py-1.5 rounded bg-gray-200 text-sm" @click="showReject=false">Cancelar</button>
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
import { ref, onMounted } from 'vue'
import { Search, Eraser } from 'lucide-vue-next'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'

const DOC_TYPES = {
  cpf: 'CPF',
  rg: 'RG',
  comprovante_endereco: 'Comprovante de Endereço',
  pis: 'PIS'
}

const docs = ref([])
const showPreview = ref(false)
const previewUrl = ref('')
const filters = ref({ licensed: '', status: '' })
const showReject = ref(false)
const rejectDoc = ref(null)
const rejectReason = ref('')

function labelType(k) { return DOC_TYPES[k] || k }
function openPreview(url) { previewUrl.value = url; showPreview.value = true }
function isPdf(url) { return /\.pdf($|\?)/i.test(url || '') }
function isImage(url) { return /\.(png|jpe?g|gif|webp|bmp|svg)($|\?)/i.test(url || '') }

async function fetchData() {
  const params = new URLSearchParams()
  if (filters.value.licensed) params.append('licensed_username', filters.value.licensed)
  if (filters.value.status) params.append('status', filters.value.status)
  const url = '/api/core/licensed-documents/pending/' + (params.toString() ? `?${params.toString()}` : '')
  const { data } = await api.get(url)
  docs.value = data || []
}

function applySearch() { fetchData() }
function clearSearch() { filters.value = { licensed: '', status: '' }; fetchData() }

async function setStatus(doc, st) {
  await api.patch(`/api/core/licensed-documents/${doc.id}/`, { stt_validate: st, rejection_reason: st==='rejected' ? (doc.rejection_reason || 'Documento inconsistente') : null })
  await fetchData()
}

function openReject(doc) { rejectDoc.value = doc; rejectReason.value = ''; showReject.value = true }
async function confirmReject() { if (!rejectDoc.value) return; await api.patch(`/api/core/licensed-documents/${rejectDoc.value.id}/`, { stt_validate: 'rejected', rejection_reason: rejectReason.value || 'Documento inconsistente' }); showReject.value = false; await fetchData() }

onMounted(fetchData)
</script>


