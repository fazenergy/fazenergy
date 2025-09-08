<template>
  <div class="space-y-3">
    <!-- Toolbar: apenas ações -->
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm" @click="show=true">Editar cadastro</button>
        <button class="px-3 py-1.5 rounded bg-orange-500 hover:bg-orange-600 text-white text-sm" @click="openResetPass">Trocar senha</button>
      </div>
    </div>

    <!-- Card de perfil (somente leitura) -->
    <div class="bg-white rounded border p-4">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        <!-- Avatar -->
        <div class="md:col-span-3 flex flex-col items-center gap-3">
          <div class="w-[128px] h-[128px] rounded-md overflow-hidden border bg-gray-100 flex items-center justify-center">
            <img v-if="displayAvatar" :src="displayAvatar" class="object-cover w-full h-full" />
          </div>
          <div class="text-xs text-gray-500 truncate max-w-[8rem]">{{ user?.username }}</div>
        </div>

        <!-- Bloco: Dados pessoais -->
        <div class="md:col-span-9">
          <div class="border rounded-lg p-4">
            <div class="text-sm font-semibold mb-3">Dados pessoais</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm">
              <div><div class="text-[12px] font-semibold text-gray-700">Nome</div><div class="mt-0.5">{{ form?.first_name }}</div></div>
              <div><div class="text-[12px] font-semibold text-gray-700">Sobrenome</div><div class="mt-0.5">{{ form?.last_name }}</div></div>
              <div><div class="text-[12px] font-semibold text-gray-700">Email</div><div class="mt-0.5 break-all">{{ form?.email }}</div></div>
              <div><div class="text-[12px] font-semibold text-gray-700">Usuário</div><div class="mt-0.5">{{ form?.username }}</div></div>
              <div><div class="text-[12px] font-semibold text-gray-700">Telefone</div><div class="mt-0.5">{{ form?.phone }}</div></div>
              <div><div class="text-[12px] font-semibold text-gray-700">CPF/CNPJ</div><div class="mt-0.5">{{ form?.cpf_cnpj }}</div></div>
            </div>
          </div>
          <!-- Bloco: Endereço -->
          <div class="border rounded-lg p-4">
            <div class="text-sm font-semibold mb-3">Endereço</div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-2 text-sm">
              <div class="md:col-span-1"><div class="text-[12px] font-semibold text-gray-700">CEP</div><div class="mt-0.5">{{ form?.cep }}</div></div>
              <div class="md:col-span-1"><div class="text-[12px] font-semibold text-gray-700">Estado</div><div class="mt-0.5">{{ displayUF }}</div></div>
              <div class="md:col-span-1"><div class="text-[12px] font-semibold text-gray-700">Cidade</div><div class="mt-0.5">{{ displayCity }}</div></div>
              <div class="md:col-span-1"><div class="text-[12px] font-semibold text-gray-700">Bairro</div><div class="mt-0.5">{{ form?.district }}</div></div>
              <div class="md:col-span-2"><div class="text-[12px] font-semibold text-gray-700">Endereço</div><div class="mt-0.5">{{ form?.address }}</div></div>
              <div class="md:col-span-1"><div class="text-[12px] font-semibold text-gray-700">Número</div><div class="mt-0.5">{{ form?.number }}</div></div>
              <div class="md:col-span-3"><div class="text-[12px] font-semibold text-gray-700">Complemento</div><div class="mt-0.5">{{ form?.complement }}</div></div>
            </div>
          </div>
        </div>
      </div>
    </div>
          </div>

  <!-- Modal Editar -->
  <Modal v-model="show" :header-blue="true" :no-header-border="true">
    <template #title>Meu Perfil</template>
    <div v-if="form" class="relative">
      <LoadingOverlay v-if="saving" />
      <div class="grid grid-cols-1 md:grid-cols-6 gap-4 text-sm">
        <!-- Avatar à esquerda -->
        <div class="md:col-span-1">
          <label class="text-xs text-gray-600">Foto</label>
          <div class="mt-1 w-28 h-28 rounded-md bg-gray-100 border overflow-hidden flex items-center justify-center">
            <img :src="previewPhoto || avatarUrl(form)" v-if="(previewPhoto || avatarUrl(form))" class="w-full h-full object-cover" />
          </div>
          <div class="mt-2">
            <button type="button" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm" @click="triggerPhoto">Trocar foto</button>
            <input ref="photo" type="file" accept="image/*" class="hidden" @change="onPhotoChange" />
          </div>
          </div>

        <!-- Form igual ao modal de edição de Licenciado -->
        <div class="md:col-span-5 grid grid-cols-1 md:grid-cols-6 gap-4">
          <FormField label="Nome" class="md:col-span-3">
            <Input v-model="form.first_name" class="text-sm" />
          </FormField>
          <FormField label="Sobrenome" class="md:col-span-3">
            <Input v-model="form.last_name" class="text-sm" />
          </FormField>

          <FormField label="Email" class="md:col-span-3">
            <Input v-model="form.email" type="email" class="text-sm" />
          </FormField>
          <FormField label="Usuário" class="md:col-span-3">
            <Input v-model="form.username" class="text-sm bg-gray-100" :disabled="true" />
          </FormField>

          <FormField label="Telefone" class="md:col-span-3">
            <Input v-model="form.phone" class="text-sm" mask="(##) #####-####" />
          </FormField>

          <FormField label="CPF / CNPJ" class="md:col-span-3">
            <Input v-model="form.cpf_cnpj" class="text-sm" mask="###.###.###-##" />
          </FormField>
          <FormField label="CEP" class="md:col-span-1">
            <Input v-model="form.cep" class="text-sm" mask="#####-###" @input="onCepInput" />
          </FormField>
          <FormField label="Estado" class="md:col-span-1">
            <Select v-model="form.state_id" class="text-sm">
              <option :value="null">Selecione</option>
              <option v-for="s in states" :key="s.id" :value="s.id">{{ s.uf }}</option>
            </Select>
          </FormField>
          <FormField label="Cidade" class="md:col-span-2">
            <Select v-model="form.city_id" class="text-sm">
              <option :value="null">Selecione a Cidade</option>
              <option v-for="c in cities" :key="c.id" :value="c.id">{{ c.name }}</option>
            </Select>
          </FormField>

          <FormField label="Bairro" class="md:col-span-2">
            <Input v-model="form.district" class="text-sm" />
          </FormField>
          <FormField label="Endereço" class="md:col-span-5">
            <Input v-model="form.address" class="text-sm" />
          </FormField>
          <FormField label="Número" class="md:col-span-1">
            <Input v-model="form.number" class="text-sm" />
          </FormField>
          <FormField label="Complemento" class="md:col-span-6">
            <Input v-model="form.complement" class="text-sm" />
          </FormField>
          </div>
          </div>
          </div>
    <template #footer>
      <div class="flex justify-end gap-2">
        <button class="px-4 py-2 rounded border text-sm" :disabled="saving" @click="show=false">Fechar</button>
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm inline-flex items-center gap-2 disabled:opacity-60" :disabled="saving" @click="saveProfile">
          <span v-if="saving" class="inline-block h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
          <span>{{ saving ? 'Gravando...' : 'Gravar' }}</span>
        </button>
          </div>
    </template>
  </Modal>

  <!-- Modal Trocar Senha -->
  <Modal v-model="showResetPass" :header-blue="true" :no-header-border="true">
    <template #title>Trocar Senha</template>
    <div class="relative" :key="rpKey">
      <div v-if="rpMsg" class="mb-3 px-3 py-2 rounded bg-blue-50 text-blue-700 border border-blue-200 text-sm relative">
        {{ rpMsg }}
        <button class="absolute right-2 top-1/2 -translate-y-1/2 text-blue-700 hover:text-blue-900" @click="rpMsg=''" aria-label="Fechar">×</button>
          </div>
      <!-- campos fantasmas contra autofill -->
      <div style="position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden;" aria-hidden="true">
        <input type="text" name="username" autocomplete="username" tabindex="-1" />
        <input type="password" name="password" autocomplete="current-password" tabindex="-1" />
          </div>
      <div class="grid grid-cols-1 md:grid-cols-6 gap-4 text-sm">
        <FormField label="Nome" class="md:col-span-3">
          <Input :model-value="form?.first_name + ' ' + form?.last_name" readonly />
        </FormField>
        <FormField label="Usuário" class="md:col-span-3">
          <Input :model-value="form?.username" readonly />
        </FormField>
        <FormField label="Senha" class="md:col-span-3">
          <InputPass v-model="rpForm.password" :name="`rp_${rpKey}_pw`" autocomplete="new-password" />
        </FormField>
        <FormField label="Confirmar Senha" class="md:col-span-3">
          <InputPass v-model="rpForm.confirm" :name="`rp_${rpKey}_confirm`" autocomplete="new-password" />
        </FormField>
        <div class="md:col-span-6 flex items-center gap-2">
          <Checkbox v-model="rpForm.forceChange" />
          <span class="text-sm">Trocar senha no próximo logon?</span>
        </div>
    </div>
    </div>
    <template #footer>
      <div class="flex justify-end gap-2">
        <button class="px-4 py-2 rounded border text-sm" :disabled="rpSaving" @click="showResetPass=false">Fechar</button>
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm inline-flex items-center gap-2 disabled:opacity-60" :disabled="rpSaving" @click="saveResetPass">
          <span v-if="rpSaving" class="inline-block h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
          <span>{{ rpSaving ? 'Gravando...' : 'Gravar' }}</span>
        </button>
  </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import FormField from '@/components/ui/FormField.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'
import InputPass from '@/components/ui/InputPass.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import { API_BASE_URL } from '@/config/settings'

const show = ref(false)
const saving = ref(false)
const user = ref(null)
const form = ref(null)
const states = ref([])
const cities = ref([])
const previewPhoto = ref('')
const photo = ref(null)
const initializing = ref(false)
const profileLic = ref(null)

onMounted(async () => {
  const { data: u } = await api.get('/api/core/profile/')
  user.value = u
  // estados
  try {
    const { data: s } = await api.get('/api/location/states/')
    states.value = s || []
  } catch {}

  // busca Licensed correspondente na lista e pega city/state/endereços
  let lic = null
  try {
    // Busca direta do Licensed do usuário atual (evita paginação da lista)
    const { data } = await api.get('/api/core/profile/licensed/')
    lic = data && data.id ? data : null
  } catch {}
  profileLic.value = lic

  form.value = {
    first_name: u.first_name || '',
    last_name: u.last_name || '',
    username: u.username || '',
    email: u.email || '',
    phone: lic?.phone || u.phone || '',
    cpf_cnpj: lic?.cpf_cnpj || u.cpf_cnpj || '',
    cep: lic?.cep || u.cep || '',
    address: lic?.address || u.address || '',
    number: lic?.number || u.number || '',
    complement: lic?.complement || u.complement || '',
    district: lic?.district || u.district || '',
    state_id: lic?.city_lookup?.state?.id || (u.city?.state?.id ?? null),
    city_id: lic?.city_lookup?.id || (u.city?.id ?? null),
  }

  // Se não houver dados do licensed via listagem, buscar via endpoint profile/licensed se existir

  previewPhoto.value = u.image_profile || ''

  initializing.value = true
  try {
    if (form.value.state_id) {
      await loadCities(form.value.state_id)
      // Se veio cidade do perfil (u.city), preserva
      if (form.value.city_id && !cities.value.find(c => c.id === form.value.city_id)) {
        const candidate = (cities.value || []).find(c => String(c.id) === String(u.city?.id))
        if (candidate) form.value.city_id = candidate.id
      }
    }
  } finally {
    initializing.value = false
  }
})

async function loadCities(stateId) {
  try {
    const { data } = await api.get('/api/location/cities/', { params: { state: stateId } })
    cities.value = data || []
  } catch {
    cities.value = []
  }
}

async function onCepInput() {
  try {
    const digits = String(form.value.cep || '').replace(/\D/g, '')
    if (digits.length !== 8) return
    const res = await fetch(`https://viacep.com.br/ws/${digits}/json/`).then(r => r.json())
    if (!res || res.erro) return
    form.value.address = res.logradouro || form.value.address
    form.value.district = res.bairro || form.value.district
    const uf = String(res.uf || '').toUpperCase()
    const state = (states.value || []).find(s => String(s.uf).toUpperCase() === uf)
    if (state) {
      form.value.state_id = state.id
      await loadCities(state.id)
      const normalize = s => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()
      const city = (cities.value || []).find(c => normalize(c.name) === normalize(res.localidade))
      if (city) form.value.city_id = city.id
    }
  } catch {}
}

watch(() => form.value?.state_id, async (nv, ov) => {
  if (nv) {
    await loadCities(nv)
    if (!initializing.value && ov !== undefined) {
      form.value.city_id = null
    }
  } else {
    cities.value = []
    form.value.city_id = null
  }
})

function avatarUrl(obj) {
  const url = obj?.image_profile || ''
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  const pref = url.startsWith('/') ? url : `/${url}`
  return `${API_BASE_URL}${pref}`
}

const displayAvatar = computed(() => previewPhoto.value || avatarUrl(user.value) )
const displayUF = computed(() => {
  try {
    const st = states.value.find(s => s.id === form.value?.state_id)
    return st?.uf || '-'
  } catch { return '-' }
})
const displayCity = computed(() => {
  try {
    const ct = cities.value.find(c => c.id === form.value?.city_id)
    return ct?.name || '-'
  } catch { return '-' }
})

function onPhotoChange(e) {
  const f = e?.target?.files?.[0]
  if (!f) { previewPhoto.value = ''; return }
  const r = new FileReader()
  r.onload = () => { previewPhoto.value = r.result }
  r.readAsDataURL(f)
}
function triggerPhoto() { try { photo.value?.click() } catch {} }

function isValidEmail(v){
  if (!v) return true
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v).toLowerCase())
}

const savingMsg = ref('')
async function saveProfile() {
  if (!isValidEmail(form.value.email)) { alert('Email inválido.'); return }
  saving.value = true
  savingMsg.value = ''
  try {
    const fd = new FormData()
    if (form.value.username && form.value.username !== (user.value?.username || '')) {
      fd.append('username', form.value.username)
    }
    fd.append('first_name', form.value.first_name || '')
    fd.append('last_name', form.value.last_name || '')
    fd.append('email', form.value.email || '')
    if (form.value.phone) fd.append('phone', form.value.phone)
    if (form.value.cpf_cnpj) fd.append('cpf_cnpj', form.value.cpf_cnpj)
    if (form.value.cep) fd.append('cep', form.value.cep)
    if (form.value.address) fd.append('address', form.value.address)
    if (form.value.number) fd.append('number', form.value.number)
    if (form.value.complement) fd.append('complement', form.value.complement)
    if (form.value.district) fd.append('district', form.value.district)
    if (form.value.city_id) fd.append('city_lookup', form.value.city_id)
    if (photo.value?.files?.[0]) fd.append('image_profile', photo.value.files[0])
    await api.patch('/api/core/profile/', fd)
    show.value = false
    alert('Perfil atualizado!')
  } catch (e) {
    const data = e?.response?.data
    let msg = 'Não foi possível salvar seu perfil.'
    if (data && typeof data === 'object') {
      try { const k = Object.keys(data)[0]; const v = Array.isArray(data[k]) ? data[k][0] : data[k]; if (k && v) msg = `${k}: ${v}` } catch {}
    }
    alert(msg)
  } finally {
    saving.value = false
  }
}

// Reset de senha (mesma regra do Licensed)
const showResetPass = ref(false)
const rpForm = ref({ password: '', confirm: '', forceChange: false })
const rpSaving = ref(false)
const rpMsg = ref('')
const rpKey = ref(0)
function openResetPass(){ rpForm.value={ password:'', confirm:'', forceChange:false }; rpMsg.value=''; rpKey.value++; showResetPass.value=true }
function isSenhaSegura(senha) { return !!senha && senha.length >= 6 && /[a-zA-Z]/.test(senha) && /\d/.test(senha) && /[^a-zA-Z0-9]/.test(senha) }
async function saveResetPass(){
  if (!isSenhaSegura(rpForm.value.password)) { rpMsg.value='Senha inválida. Use ao menos 6 caracteres, com letra, número e símbolo.'; return }
  if (rpForm.value.password !== rpForm.value.confirm) { rpMsg.value='As senhas não coincidem.'; return }
  rpSaving.value = true
  try {
    const fd = new FormData(); fd.append('password', rpForm.value.password)
    await api.patch('/api/core/profile/', fd)
    showResetPass.value = false
  } catch (e) { rpMsg.value = 'Não foi possível trocar a senha.' } finally { rpSaving.value = false }
}
</script>

