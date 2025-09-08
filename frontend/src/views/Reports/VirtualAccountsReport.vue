<template>
  <div class="space-y-3">
    <!-- Toolbar padrão: Exportar/Imprimir e busca -->
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <FileDown class="w-4 h-4" />
          <span>Exportar</span>
        </button>
        <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
          <Printer class="w-4 h-4" />
          <span>Imprimir</span>
        </button>

        <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
          <input v-model.trim="q" type="text" placeholder="Pesquisar por nome ou login..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
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
      <DataTable :columns="columns" :rows="rows" :loading="loading" :min-height="gridMinHeight">
        <template #title>Contas Virtuais</template>
        <template #actions="{ row }">
          <div class="flex items-center gap-1">
            <button class="inline-flex items-center justify-center w-8 h-8 rounded border border-gray-300 bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-800" @click="openReport(row)" title="Resumo Analítico">
              <FileText class="w-4 h-4" />
            </button>
          </div>
        </template>
        <template #col:avatar="{ row }">
          <img :src="avatarUrl(row)" class="w-8 h-8 rounded-full object-cover" loading="lazy" />
        </template>
        <template #col:nameLogin="{ row }">
          <div class="text-[12px] leading-tight">
            <div>{{ row.user?.full_name || fullName(row) || '-' }}</div>
            <div><b>Login:</b> {{ row.user?.username || '-' }}</div>
          </div>
        </template>
        <template #col:dtt_update="{ row }">{{ formatDate(row.virtual_account?.dtt_update) }}</template>
        <template #col:balance="{ row }">
          <div class="text-center">R$ {{ Number(row.virtual_account?.balance_available || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
        </template>
        <template #col:withdraw="{ row }">
          <span :class="row.has_withdraw_request ? 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-100 text-amber-800 border border-amber-300' : 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-700 border border-gray-300'">
            {{ row.has_withdraw_request ? 'Sim' : 'Não' }}
          </span>
        </template>
      </DataTable>
    </div>

    <!-- Modal Relatório (reuso do de Licenciados) -->
    <Modal v-model="showReport" :header-blue="true" :no-header-border="true">
      <template #title>Relatório do Licenciado</template>
      <div v-if="current">
        <!-- Renderizamos o mesmo cabeçalho do relatório já existente -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div><b>Nome Completo:</b> {{ fullName(current) }}</div>
          <div><b>Login:</b> {{ current.user?.username }}</div>
          <div><b>Plano atual:</b> {{ current.plan?.name || '-' }}</div>
          <div><b>Data de ativação:</b> {{ formatDate(current.dtt_activation) }}</div>
          <div><b>Saldo conta virtual:</b> R$ {{ (current.virtual_account?.balance_available || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</div>
          <div><b>Status documentação PF:</b> {{ docLabel(current.stt_document) }}</div>
        </div>
        <div class="mt-4">
          <div class="text-sm font-semibold mb-2">Upline</div>
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-blue-800 text-white">
                <th class="px-3 py-2 text-left">Upline</th>
                <th class="px-3 py-2 text-right">Nível</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in reportUpline" :key="u.id" class="even:bg-gray-50">
                <td class="px-3 py-2">{{ u.full_name || u.username }} <span class="text-gray-500">| {{ u.username }}</span></td>
                <td class="px-3 py-2 text-right">{{ u.level }}</td>
              </tr>
              <tr v-if="!reportUpline.length">
                <td colspan="2" class="px-3 py-4 text-center text-gray-500">Sem upline.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/services/axios'
import { API_BASE_URL } from '@/config/settings'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import { FileText, FileDown, Printer, Search, Eraser } from 'lucide-vue-next'

const rows = ref([])
const all = ref([])
const q = ref('')
const loading = ref(false)
const showReport = ref(false)
const current = ref(null)
const reportUpline = ref([])

const columns = [
  { key: 'avatar', label: 'Avatar', width: 'w-[64px]' },
  { key: 'nameLogin', label: 'Nome/Login' },
  { key: 'dtt_update', label: 'Dtt Atualização' },
  { key: 'balance', label: 'Saldo', align: 'center' },
  { key: 'withdraw', label: 'Solic. Saque' },
]

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}

function formatDate(dt) {
  try {
    if (!dt) return '-'
    const d = new Date(dt)
    if (isNaN(d.getTime())) return '-'
    return d.toLocaleString('pt-BR')
  } catch { return '-' }
}
function fullName(lic) { return (lic.user?.first_name||'') + ' ' + (lic.user?.last_name||'') }
function docLabel(st) { return ({ pending: 'Pendente', incomplete: 'Incompleto', awaiting: 'Aguardando aprovação', approved: 'Aprovado', rejected: 'Reprovado' })[st] || '-' }

function avatarUrl(obj) {
  const user = obj?.user || obj
  const url = user?.image_profile || user?.image || user?.avatar || obj?.avatar || obj?.image || obj?.image_profile || ''
  if (!url) return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="100%" height="100%" fill="%23e5e7eb"/></svg>'
  if (/^https?:\/\//i.test(url)) return url
  const pref = url.startsWith('/') ? url : `/${url}`
  return `${API_BASE_URL}${pref}`
}

const filtered = computed(() => {
  const term = (q.value || '').toLowerCase()
  return (all.value || []).filter(lic => !term || (lic.user?.username||'').toLowerCase().includes(term) || ((lic.user?.first_name||'') + ' ' + (lic.user?.last_name||'')).toLowerCase().includes(term))
})

watch(filtered, () => {
  // paginação simples: mantemos tudo em rows
  rows.value = filtered.value
})

function applySearch() {}
function clearSearch() { q.value = '' }

async function openReport(row) {
  current.value = row
  showReport.value = true
  try {
    const { data } = await api.get('/api/network/upline-chain/', { params: { licensed_id: row.id } })
    reportUpline.value = data?.chain || []
  } catch { reportUpline.value = [] }
}

async function loadData() {
  loading.value = true
  try {
    // 1) Busca a lista base de licenciados (leve)
    const { data } = await api.get('/api/core/licensed/')
    const base = data?.results || data || []

    // 2) Enriquecimento paralelo: saldo/atualização e flag de solicitação de saque
    const enriched = await Promise.all(base.map(async (lic) => {
      try {
        const [balRes, saqRes] = await Promise.all([
          api.get('/api/finance/virtual-account/balance/', { params: { licensed_id: lic.id } }),
          api.get('/api/finance/transactions/', { params: { licensed_username: lic.user?.username, month: new Date().getMonth()+1, year: new Date().getFullYear() } })
        ])
        const balance_available = balRes?.data?.balance_available || 0
        const balance_blocked = balRes?.data?.balance_blocked || 0
        const has_withdraw_request = (saqRes?.data || []).some(t => String(t.product||'').toLowerCase().includes('saque'))
        const dtt_update = lic.dtt_update || null
        return {
          ...lic,
          virtual_account: { balance_available, balance_blocked, dtt_update },
          has_withdraw_request,
        }
      } catch {
        return { ...lic, virtual_account: { balance_available: 0, balance_blocked: 0 }, has_withdraw_request: false }
      }
    }))
    all.value = enriched
    rows.value = enriched
  } catch {
    all.value = []
    rows.value = []
  } finally {
    loading.value = false
    updateGridHeight()
  }
}

function exportExcel() {
  const header = ['Nome', 'Login', 'Dtt Atualização', 'Saldo', 'Solic. Saque']
  const rowsHtml = (rows.value || []).map(r => (
    `<tr>`+
    `<td>${(r.user?.full_name||'').replace(/</g,'&lt;')}</td>`+
    `<td>${(r.user?.username||'')}</td>`+
    `<td>${formatDate(r.virtual_account?.dtt_update)}</td>`+
    `<td>${Number(r.virtual_account?.balance_available||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>`+
    `<td>${r.has_withdraw_request ? 'Sim' : 'Não'}</td>`+
    `</tr>`
  )).join('')
  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `contas_virtuais.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = (rows.value || []).map(r => (
    `<tr>`+
    `<td>${(r.user?.full_name||'')}</td>`+
    `<td>${(r.user?.username||'')}</td>`+
    `<td>${formatDate(r.virtual_account?.dtt_update)}</td>`+
    `<td style="text-align:right">${Number(r.virtual_account?.balance_available||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>`+
    `<td>${r.has_withdraw_request ? 'Sim' : 'Não'}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Contas Virtuais</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Contas Virtuais</h3>
    <table>
      <thead><tr><th>Nome</th><th>Login</th><th>Dtt Atualização</th><th>Saldo</th><th>Solic. Saque</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

onMounted(loadData)
</script>

<style scoped>
</style>


