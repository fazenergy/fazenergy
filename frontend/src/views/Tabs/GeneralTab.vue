<template>
  <div class="space-y-3">
    <!-- Abas internas -->
    <div class="flex border-b mb-2 space-x-2">
      <button :class="['px-4 py-2 rounded-t', active==='Empresa' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Empresa'">Empresa</button>
      <button :class="['px-4 py-2 rounded-t', active==='Logo Principal' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Logo Principal'">Logo Principal</button>
      <button :class="['px-4 py-2 rounded-t', active==='Logo Sidebar' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Logo Sidebar'">Logo Sidebar</button>
      <button :class="['px-4 py-2 rounded-t', active==='Ícone' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Ícone'">Logo ICO</button>
      <button :class="['px-4 py-2 rounded-t', active==='Logo Login' ? 'bg-green-600 text-white border border-b-0' : 'bg-gray-100 hover:bg-gray-200']" @click="active='Logo Login'">Logo Login</button>
    </div>

    <!-- Conteúdo da sub-aba selecionada -->
    <div class="p-3 bg-white rounded">
      <!-- Empresa -->
      <template v-if="active==='Empresa'">
        <div class="flex items-start md:items-center justify-between mb-3">
          <h3 class="text-sm font-semibold">Informações da Empresa</h3>
          <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-gray-500">Nome da Empresa</label>
            <input v-model.trim="form.company_name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">CNPJ</label>
            <input v-model.trim="form.cnpj" class="w-full border rounded px-2 py-1 h-8 text-sm" placeholder="00.000.000/0000-00" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Telefone</label>
            <input v-model.trim="form.phone" class="w-full border rounded px-2 py-1 h-8 text-sm" placeholder="(00) 00000-0000" />
          </div>
          <div>
            <label class="text-xs text-gray-500">CEP</label>
            <input v-model.trim="form.cep" class="w-full border rounded px-2 py-1 h-8 text-sm" placeholder="00000-000" />
          </div>
          <div class="md:col-span-2">
            <label class="text-xs text-gray-500">Endereço</label>
            <input v-model.trim="form.address" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Número</label>
            <input v-model.trim="form.number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Bairro</label>
            <input v-model.trim="form.district" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Cidade</label>
            <input v-model.trim="form.city" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
          <div>
            <label class="text-xs text-gray-500">Estado (UF)</label>
            <input v-model.trim="form.state" class="w-full border rounded px-2 py-1 h-8 text-sm" />
          </div>
        </div>
        <p class="mt-2 text-[11px] text-gray-500">Os dados são salvos localmente até existir persistência no servidor.</p>
      </template>

      <!-- Logo Principal -->
      <template v-else-if="active==='Logo Principal'">
        <div class="flex items-start md:items-center justify-between mb-3">
          <h3 class="text-sm font-semibold">Logo Principal</h3>
          <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
        </div>
        <div class="flex items-center gap-3">
          <div class="w-24 h-24 border rounded bg-gray-50 flex items-center justify-center overflow-hidden">
            <img v-if="logoPreview" :src="logoPreview" alt="logo" class="object-cover w-full h-full" />
            <span v-else class="text-[10px] text-gray-400">Sem logo</span>
          </div>
          <div class="flex-1">
            <input type="file" accept="image/*" @change="onLogoChange" class="w-full text-xs" />
            <button v-if="logoPreview" @click="clearLogo" class="mt-1 text-xs underline">Remover</button>
          </div>
        </div>
      </template>

      <!-- Logo Sidebar -->
      <template v-else-if="active==='Logo Sidebar'">
        <div class="flex items-start md:items-center justify-between mb-3">
          <h3 class="text-sm font-semibold">Logo Sidebar</h3>
          <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
        </div>
        <div class="space-y-4">
          <!-- Normal -->
          <div class="flex items-center gap-3">
            <div class="w-28 h-12 border rounded bg-gray-50 flex items-center justify-center overflow-hidden">
              <img v-if="logoSidebarPreview" :src="logoSidebarPreview" alt="logo-sidebar" class="object-contain w-full h-full" />
              <span v-else class="text-[10px] text-gray-400">Sem logo</span>
            </div>
            <div class="flex-1">
              <label class="text-xs text-gray-500">Logo Sidebar (normal)</label>
              <input type="file" accept="image/*" @change="onLogoSidebarChange" class="w-full text-xs" />
              <button v-if="logoSidebarPreview" @click="clearLogoSidebar" class="mt-1 text-xs underline">Remover</button>
            </div>
          </div>

          <!-- Mini (sidebar recolhida) -->
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 border rounded bg-gray-50 flex items-center justify-center overflow-hidden">
              <img v-if="logoSidebarMiniPreview" :src="logoSidebarMiniPreview" alt="logo-sidebar-mini" class="object-contain w-full h-full" />
              <span v-else class="text-[10px] text-gray-400">Sem logo</span>
            </div>
            <div class="flex-1">
              <label class="text-xs text-gray-500">Logo Sidebar (mini)</label>
              <input type="file" accept="image/*" @change="onLogoSidebarMiniChange" class="w-full text-xs" />
              <button v-if="logoSidebarMiniPreview" @click="clearLogoSidebarMini" class="mt-1 text-xs underline">Remover</button>
            </div>
          </div>
        </div>
      </template>

      <!-- Ícone -->
      <template v-else-if="active==='Ícone'">
        <div class="flex items-start md:items-center justify-between mb-3">
          <h3 class="text-sm font-semibold">Ícone do Navegador (Favicon)</h3>
          <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
        </div>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 border rounded bg-gray-50 flex items-center justify-center overflow-hidden">
            <img v-if="faviconPreview" :src="faviconPreview" alt="favicon" class="object-contain w-full h-full" />
            <span v-else class="text-[10px] text-gray-400">Sem ícone</span>
          </div>
          <div class="flex-1">
            <input type="file" accept="image/*" @change="onFaviconChange" class="w-full text-xs" />
            <button v-if="faviconPreview" @click="clearFavicon" class="mt-1 text-xs underline">Remover</button>
          </div>
        </div>
      </template>

      <!-- Logo Login -->
      <template v-else>
        <div class="flex items-start md:items-center justify-between mb-3">
          <h3 class="text-sm font-semibold">Logo para Modal de Login</h3>
          <button @click="save" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white">Gravar</button>
        </div>
        <div class="flex items-center gap-3">
          <div class="w-32 h-20 border rounded bg-gray-50 flex items-center justify-center overflow-hidden">
            <img v-if="logoLoginPreview" :src="logoLoginPreview" alt="logo-login" class="object-contain w-full h-full" />
            <span v-else class="text-[10px] text-gray-400">Sem logo</span>
          </div>
          <div class="flex-1">
            <input type="file" accept="image/*" @change="onLogoLoginChange" class="w-full text-xs" />
            <button v-if="logoLoginPreview" @click="clearLogoLogin" class="mt-1 text-xs underline">Remover</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
// Aba Geral: integra com o store de configurações para salvar/carregar.
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/store/settings'

// Instância do store
const settingsStore = useSettingsStore()

// Estado local do formulário (edição desacoplada)
const form = ref({ company_name: '', cnpj: '', phone: '', address: '', number: '', district: '', city: '', state: '', cep: '' })
const logoPreview = ref(null)
const logoSidebarPreview = ref(null)
const faviconPreview = ref(null)
const logoLoginPreview = ref(null)
const active = ref('Empresa')

onMounted(() => {
  // Carrega do storage via store e popula o formulário
  settingsStore.loadFromStorage()
  form.value = { ...form.value, ...settingsStore.settings.general }
  logoPreview.value = settingsStore.settings.general.logo_data_url || null
  logoSidebarPreview.value = settingsStore.settings.general.logo_sidebar_data_url || null
  logoSidebarMiniPreview.value = settingsStore.settings.general.logo_sidebar_mini_data_url || null
  faviconPreview.value = settingsStore.settings.general.favicon_data_url || null
  logoLoginPreview.value = settingsStore.settings.general.logo_login_data_url || null
})

function onLogoChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  // Para manter a persistência local, convertemos a imagem para DataURL
  const reader = new FileReader()
  reader.onload = () => {
    logoPreview.value = reader.result
  }
  reader.readAsDataURL(f)
}

function clearLogo() {
  logoPreview.value = null
}

function onLogoSidebarChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const reader = new FileReader()
  reader.onload = () => { logoSidebarPreview.value = reader.result }
  reader.readAsDataURL(f)
}
function clearLogoSidebar() { logoSidebarPreview.value = null }

// Sidebar (mini)
const logoSidebarMiniPreview = ref(null)
function onLogoSidebarMiniChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const reader = new FileReader()
  reader.onload = () => { logoSidebarMiniPreview.value = reader.result }
  reader.readAsDataURL(f)
}
function clearLogoSidebarMini() { logoSidebarMiniPreview.value = null }

function onFaviconChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const reader = new FileReader()
  reader.onload = () => { faviconPreview.value = reader.result }
  reader.readAsDataURL(f)
}
function clearFavicon() { faviconPreview.value = null }

function onLogoLoginChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  const reader = new FileReader()
  reader.onload = () => { logoLoginPreview.value = reader.result }
  reader.readAsDataURL(f)
}
function clearLogoLogin() { logoLoginPreview.value = null }

function save() {
  // Atualiza bloco "general" no store e persiste
  settingsStore.setGeneral({
    ...form.value,
    logo_data_url: logoPreview.value,
    logo_sidebar_data_url: logoSidebarPreview.value,
    logo_sidebar_mini_data_url: logoSidebarMiniPreview.value,
    favicon_data_url: faviconPreview.value,
    logo_login_data_url: logoLoginPreview.value,
  })
  settingsStore.saveToStorage()
  alert('Configurações gerais salvas.')
}
</script>


