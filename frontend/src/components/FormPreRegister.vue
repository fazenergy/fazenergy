<template>
  <div class="space-y-6">
    <!-- Sucesso de cadastro: card/alert -->
    <div v-if="showSuccess" class="border-l-4 border-emerald-500 bg-emerald-50 text-emerald-800 p-4 rounded">
      <div class="flex items-center justify-between gap-3">
        <div>
          <div class="font-semibold">{{ successMessage.title }}</div>
          <div class="text-sm">{{ successMessage.body }}</div>
        </div>
        <div class="flex items-center gap-2">
          <button @click="openPaymentNow" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Pagar Agora</button>
          <button @click="showSuccess=false" class="px-3 py-1.5 rounded border text-sm">Fechar</button>
        </div>
      </div>
    </div>
    <!-- Alert flutuante para regras de senha -->
    <div v-if="passwordAlerts.length && showPasswordAlert && (form.password?.length > 0)" class="fixed md:top-4 md:right-4 top-2 right-2 z-50 max-w-md shadow-lg pointer-events-auto">
      <div class="relative rounded border border-red-200 bg-red-50 text-red-700 px-4 py-3">
        <button type="button" @click="showPasswordAlert = false" class="absolute top-1 right-2 text-red-500/70 hover:text-red-700 text-lg">×</button>
        <strong class="font-semibold">Atenção</strong>
        <ul class="list-disc ml-5 mt-1 text-sm">
          <li v-for="(msg, idx) in passwordAlerts" :key="idx">{{ msg }}</li>
        </ul>
      </div>
    </div>
    <div v-if="!referrerValid" class="text-red-500 text-center mb-4">
      {{ referrerError }}
    </div>
    <div class="bg-white rounded-lg p-4 md:p-6 relative">
      <LoadingOverlay v-if="loading" message="Processando..." />
      <div v-if="completed" class="min-h-[220px] grid place-items-center text-center p-6">
        <div class="max-w-xl">
          <div class="text-emerald-700 font-semibold text-lg">Cadastro realizado com sucesso!</div>
          <div class="text-gray-600 mt-1">Enviamos o contrato e o link de pagamento para o e-mail informado. Você pode abrir o pagamento agora para concluir a ativação.</div>
          <div class="mt-4 flex items-center justify-center gap-2">
            <button @click="openPaymentNow" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">Pagar Agora</button>
            <button @click="emitClose" class="px-4 py-2 rounded border">Fechar</button>
          </div>
        </div>
      </div>
    <form v-else id="preRegisterForm" @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-6 gap-4">

      <!-- Linha 1 -->
      <FormField label="Indicado por" class="md:col-span-2" :error="errors.referrer">
        <div class="relative">
          <div class="flex items-center">
            <Input v-model="form.referrer" :readonly="lockReferrer" class="bg-gray-100 text-sm" @input="onReferrerInput" @focus="onReferrerFocus" @blur="onReferrerBlur" />
            <button v-if="!lockReferrer" type="button" class="ml-2 px-2 py-1 text-xs rounded border hover:bg-gray-50" @click="manualLookup">
              🔍
            </button>
          </div>
          <div v-if="showReferrerDropdown && suggestions.length" class="absolute z-10 mt-1 w-full bg-white border rounded shadow-sm max-h-56 overflow-auto">
            <div v-for="s in suggestions" :key="s.username" class="px-3 py-2 text-sm hover:bg-gray-50 cursor-pointer" @mousedown.prevent="pickReferrer(s.username)">
              <span class="font-medium">{{ s.username }}</span>
              <span v-if="s.full_name" class="text-gray-500"> — {{ s.full_name }}</span>
            </div>
          </div>
        </div>
      </FormField>
      <FormField label="Nome Completo" class="md:col-span-3" :error="errors.full_name">
        <Input v-model="form.full_name" placeholder="Seu nome completo" required class="text-sm" />
      </FormField>
      <div class="md:col-span-1 flex items-center pt-6">
        <Switch v-model="form.is_root" :disabled="!isAdmin" />
        <span class="ml-2 text-sm">Indicador raiz</span>
      </div>

      <!-- Linha 2 -->
      <FormField label="Email" class="md:col-span-2" :error="errors.email">
        <Input v-model="form.email" type="email" required class="text-sm" />
      </FormField>
      <FormField label="Usuário" class="md:col-span-2" :error="errors.username">
        <Input v-model="form.username" required class="text-sm" />
      </FormField>
      <FormField label="Senha" class="md:col-span-1" :error="errors.password">
        <InputPass v-model="form.password" required @focus="showPasswordAlert = true" @blur="showPasswordAlert = false" />
      </FormField>
      <FormField label="Confirmar" class="md:col-span-1" :error="errors.confirm_password">
        <InputPass v-model="form.confirm_password" required />
      </FormField>

      <!-- Linha 3 -->
      <FormField label="Telefone" class="md:col-span-2" :error="errors.phone">
        <Input v-model="form.phone" mask="(##) #####-####" placeholder="(00) 00000-0000" class="text-sm" />
      </FormField>
      <FormField label="Tipo de Pessoa" class="md:col-span-2" :error="errors.person_type">
        <Select v-model="form.person_type" required class="text-sm">
          <option disabled value="">Selecione</option>
          <option value="pf">Pessoa Física</option>
          <option value="pj">Pessoa Jurídica</option>
        </Select>
      </FormField>
      <FormField label="CPF / CNPJ" class="md:col-span-2" :error="errors.cpf_cnpj">
        <Input v-model="form.cpfCnpj" v-mask="['###.###.###-##', '##.###.###/####-##']" placeholder="000.000.000-00" class="text-sm" />
      </FormField>

      <!-- Linha 4 -->
      <FormField label="CEP" class="md:col-span-1" :error="errors.cep">
        <Input
          v-model="form.cep"
          mask="#####-###"
          placeholder="00000-000"
          class="text-sm"
          @input="fetchAddress"
        />
      </FormField>
      <FormField label="Estado" class="md:col-span-1" :error="errors.state">
      <Select v-model="form.state" required class="text-sm">
        <option disabled value="">Selecione</option>
        <option v-for="estado in estados" :key="estado.id" :value="String(estado.id)">
          {{ estado.uf }}
        </option>
      </Select>
    </FormField>
    <FormField label="Cidade" class="md:col-span-2" :error="errors.city">
     <Select v-model="form.city" required class="text-sm">
      <option disabled value="">Selecione a Cidade</option>
      <option v-for="cidade in cidades" :key="cidade.id" :value="String(cidade.id)">
        {{ cidade.name }}
      </option>
    </Select>
    </FormField>
      <FormField label="Bairro" class="md:col-span-2" :error="errors.district">
        <Input v-model="form.district" class="text-sm" />
      </FormField>

      <!-- Linha 5 -->
      <FormField label="Endereço" class="md:col-span-3" :error="errors.address">
        <Input v-model="form.address" class="text-sm" />
      </FormField>
      <FormField label="Número" class="md:col-span-1" :error="errors.number">
        <Input v-model="form.number" class="text-sm" />
      </FormField>
      <FormField label="Complemento" class="md:col-span-2" :error="errors.complement">
        <Input v-model="form.complement" class="text-sm" />
      </FormField>

      <!-- Linha 6 -->
      <FormField label="Plano" class="md:col-span-4" :error="errors.plan">
        <Select v-model="form.plan" class="text-sm" required>
          <option disabled value="">Selecione o Plano</option>
          <option v-for="plan in plans" :key="plan.id" :value="plan.id">{{ plan.name }}</option>
        </Select>
      </FormField>
      <div class="flex items-center md:col-span-2">
        <Checkbox v-model="form.accept_lgpd" />
        <span class="ml-2 text-sm">Li e aceito a <a href="#"> política de privacidade </a> </span>
      </div>

      <!-- Separador -->
      <div v-if="!inModal" class="md:col-span-6">
        <hr class="my-4 border-gray-200" />
      </div>

      <!--  Botão (oculto quando usado no modal) -->
      <div v-if="!inModal" class="md:col-span-6 flex justify-end">
        <Button type="submit" class="px-6" :disabled="loading || completed">Gravar</Button>
      </div>
    </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import api from '@/services/axios'

// COMPONENTES
import Input from '@/components/ui/Input.vue'
import InputPass from '@/components/ui/InputPass.vue'
import Select from '@/components/ui/Select.vue'
import Button from '@/components/ui/Button.vue'
import Switch from '@/components/ui/Switch.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import FormField from '@/components/ui/FormField.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'

// PROP
const props = defineProps({
  referrerUsername: {
    type: String,
    default: ''
  },
  inModal: {
    type: Boolean,
    default: false
  }
})

// AUTH
const auth = useAuthStore()
const emit = defineEmits(['close','completed'])
const isSuperUser = computed(() => auth.user?.is_superuser)
const isAdmin = computed(() => auth.user?.is_superuser || (auth.user?.groups || []).includes('Administrador'))
const isAuthenticated = computed(() => !!auth.user)
const isVisitor = computed(() => !isAuthenticated.value)
const isLicensed = computed(() => (auth.user?.groups || []).includes('Licenciado'))
const lockReferrer = computed(() => (isAuthenticated.value && isLicensed.value) || (!!props.referrerUsername && isVisitor.value))

// 🔐 Indicador atual (usuário logado ou username da URL)
const currentUser = computed(() => {
  // Se o indicador é inválido, retorna vazio
  if (!referrerValid.value) return ''
  // Sempre mostra o username da URL se visitante
  if (!isAuthenticated.value && props.referrerUsername) {
    return props.referrerUsername
  }
  // Se logado, mostra o username do usuário logado
  return auth.user?.username || ''
})

const plans = ref([])
const loading = ref(false)
const referrerValid = ref(true)
const referrerError = ref('')
const suggestions = ref([] as Array<{ username: string; full_name?: string }>)
const showReferrerDropdown = ref(false)
let referrerDebounce: any = null

const form = ref({
  referrer: '', // Indicado por, será preenchido automaticamente
  full_name: '',
  email: '',
  username: '',
  password: '',
  confirm_password: '',
  phone: '',
  person_type: '',
  cpfCnpj: '',
  cep: '',
  state: '',
  city: '',
  district: '',
  address: '',
  number: '',
  complement: '',
  plan: '',
  accept_lgpd: false,
  is_root: false,
})

const errors = ref({
  referrer: '',
  full_name: '',
  email: '',
  username: '',
  password: '',
  confirm_password: '',
  phone: '',
  person_type: '',
  cpf_cnpj: '',
  cep: '',
  state: '',
  city: '',
  district: '',
  address: '',
  number: '',
  plan: '',
})

const passwordAlerts = ref<string[]>([])
const showPasswordAlert = ref(false)
const completed = ref(false)

onMounted(async () => {
  resetForm()
  try {
    const res = await api.get('/api/plans/plans/')
    plans.value = (res.data || []).filter((p:any) => p.stt_record === true)
  } catch (err) {
    plans.value = []
  }

  // ✅ Se visitante, valida username do indicador; se superadmin logado, deixa campo livre
  if (props.referrerUsername && !isSuperUser.value) {
    try {
      const resp = await api.get(`/api/users/validate-referrer/${props.referrerUsername}/`)
      if (!resp.data.valid) {
        referrerValid.value = false
        referrerError.value = 'Usuário indicador inválido.'
      } else {
        referrerValid.value = true
        form.value.referrer = props.referrerUsername // Preenche o campo automaticamente
      }
    } catch (err) {
      // Sempre mostra mensagem de usuário inválido, mesmo se der erro 401, 404, etc
      referrerValid.value = false
      referrerError.value = 'Usuário indicador inválido.'
    }
  }

  // Se logado como licenciado, trava e preenche apenas o indicadopor; email/senha ficam vazios
  if (isAuthenticated.value && isLicensed.value) {
    referrerValid.value = true
    form.value.referrer = auth.user?.username || ''
    form.value.email = ''
    form.value.password = ''
    form.value.confirm_password = ''
  }

  // Carrega estados
  const resEstados = await api.get('/api/location/states/')
  estados.value = resEstados.data

  // só usar em caso do form já ter que vier preenchido
  // if (form.value.state) {
  //   await onEstadoChange();
  // }
});

function resetForm() {
  form.value = {
    referrer: '',
    full_name: '',
    email: '',
    username: '',
    password: '',
    confirm_password: '',
    phone: '',
    person_type: '',
    cpfCnpj: '',
    cep: '',
    state: '',
    city: '',
    district: '',
    address: '',
    number: '',
    complement: '',
    plan: '',
    accept_lgpd: false,
    is_root: false,
  }
  Object.keys(errors.value).forEach(k => errors.value[k] = '')
  // evita abrir o alerta no carregamento inicial
  passwordAlerts.value = []
  showPasswordAlert.value = false
}
// Preenchimento automatico conforme CEP informado
async function fetchAddress() {
  loading.value = true
  const cep = form.value.cep.replace(/\D/g, '');
  if (cep.length === 8) {
    const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`).then(r => r.json());
    if (!res.erro) {
      form.value.address = `${res.logradouro || ''}`.trim();
      form.value.district = res.bairro || '';

      // Comparação de UF em caixa alta
      const estadoEncontrado = estados.value.find(
        e => (e.uf || '').toUpperCase() === (res.uf || '').toUpperCase()
      );
      if (estadoEncontrado) {
        form.value.state = String(estadoEncontrado.id); // <-- sempre string
        await onEstadoChange();

        // Encontrar a cidade pelo nome retornado
        const normalize = (s) => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
        const cidadeEncontrada = cidades.value.find(
          c => normalize(c.name) === normalize(res.localidade)
        );
        if (cidadeEncontrada) {
          form.value.city = String(cidadeEncontrada.id); // <-- sempre string
        }
      } else {
        form.value.state = '';
        cidades.value = [];
        form.value.city = '';
      }
    }
  }
  loading.value = false
}
function openPaymentNow() {
  // Tenta abrir o payment link mais recente do usuário criado
  const username = form.value.username
  if (!username) { return }
  // redireciona para a tela de pagamento que ajusta zoom/iframe; busca pelo username quando adesion ainda não está no contexto
  window.location.href = `/payment?licensed=${encodeURIComponent(username)}`
}

function emitClose(){
  emit('close')
}

async function doLookup(term: string) {
  if (!term || lockReferrer.value) { suggestions.value = []; return }
  try {
    const { data } = await api.get('/api/core/lookup/licensed/', { params: { q: term } })
    suggestions.value = data || []
  } catch { suggestions.value = [] }
}

function onReferrerInput(e: any) {
  if (lockReferrer.value) return
  const val = (e?.target?.value || '').trim()
  clearTimeout(referrerDebounce)
  referrerDebounce = setTimeout(() => doLookup(val), 250)
  showReferrerDropdown.value = !!val
}

function onReferrerFocus() {
  if (!lockReferrer.value && form.value.referrer) {
    showReferrerDropdown.value = true
    doLookup(form.value.referrer)
  }
}

function onReferrerBlur() {
  // fecha após pequeno delay para permitir clique
  setTimeout(() => showReferrerDropdown.value = false, 150)
}

function pickReferrer(username: string) {
  form.value.referrer = username
  showReferrerDropdown.value = false
}

function manualLookup() {
  if (lockReferrer.value) return
  doLookup(form.value.referrer)
  showReferrerDropdown.value = true
}


const estados = ref([])
const cidades = ref([])

async function onEstadoChange() {
  if (form.value.state) {
    const resCidades = await api.get(`/api/location/cities/?state=${form.value.state}`);
    cidades.value = resCidades.data;
    // Limpa cidade selecionada se não existir mais
    if (!cidades.value.find(c => String(c.id) === String(form.value.city))) {
      form.value.city = '';
    }
  } else {
    cidades.value = [];
    form.value.city = '';
  }
}

watch(() => form.value.state, async () => {
  await onEstadoChange();
});


// PERSIST: Função de envio do formulário
async function handleSubmit() {
  loading.value = true
  if (!referrerValid.value) return;
  if (passwordError.value || confirmPasswordError.value) return;

  // Limpa mensagens anteriores
  Object.keys(errors.value).forEach(k => errors.value[k] = '')

  // Validação simples dos obrigatórios
  const required = [
    ['referrer', 'obrigatório'],
    ['full_name', 'obrigatório'],
    ['email', 'obrigatório'],
    ['username', 'obrigatório'],
    ['password', 'obrigatório'],
    ['confirm_password', 'obrigatório'],
    ['phone', 'obrigatório'],
    ['person_type', 'obrigatório'],
    ['cpfCnpj', 'obrigatório'],
    ['cep', 'obrigatório'],
    ['state', 'obrigatório'],
    ['city', 'obrigatório'],
    ['district', 'obrigatório'],
    ['address', 'obrigatório'],
    ['number', 'obrigatório'],
    ['plan', 'obrigatório'],
  ]
  let hasError = false
  for (const [field, msg] of required) {
    // @ts-ignore
    if (!form.value[field]) {
      hasError = true
      // mapeia nomes
      const map = { cpfCnpj: 'cpf_cnpj' }
      const key = map[field] || field
      // @ts-ignore
      errors.value[key] = msg
    }
  }
  if (hasError) return

  // Crie uma cópia do form para não alterar o original
  const payload = { ...form.value };

  // Remova caracteres especiais dos campos
  payload.phone = payload.phone.replace(/\D/g, '').slice(0, 14); // só números, máximo 14
  payload.cpf_cnpj = (payload.cpfCnpj || '').replace(/\D/g, ''); // só números
  payload.cep = (payload.cep || '').replace(/\D/g, '').slice(0, 8); // só números, máximo 8

  // Ajuste os nomes dos campos para bater com o backend
  payload.cpf_cnpj = payload.cpfCnpj;
  payload.plan = Number(payload.plan); 
  payload.city_lookup = payload.city;
  payload.state_abbr = estados.value.find(e => String(e.id) === payload.state)?.uf || '';

if (!payload.plan) {
  alert('Selecione um plano!');
  return;
}

  // Monte o objeto user
  payload.user = {
    username: payload.username,
    email: payload.email,
    password: payload.password,
  };

  // Remova campos que não existem no backend
  delete payload.cpfCnpj;
  delete payload.city;
  delete payload.state;
  delete payload.email;
  delete payload.username;
  delete payload.password;
  delete payload.confirm_password;

  try {
    // envia apenas campos esperados pelo backend; 'referrer' é usado, mas removido antes de criar Licensed
    const { referrer, ...rest } = payload
    await api.post('/api/users/pre-register/', { ...rest, referrer });
    completed.value = true
    emit('completed')
  } catch (error) {
    alert('Erro ao cadastrar. Verifique os dados e tente novamente.');
  }
  loading.value = false
}


// validação de senha
const passwordError = ref('')
const confirmPasswordError = ref('')

function isSenhaSegura(senha) {
  // Alfanumérica, pelo menos 1 letra, 1 número, 1 caractere especial, mínimo 6 dígitos
  return (
    senha.length >= 6 &&
    /[a-zA-Z]/.test(senha) &&
    /\d/.test(senha) &&
    /[^a-zA-Z0-9]/.test(senha)
  )
}

watch(() => form.value.password, (senha) => {
  const msgs: string[] = []
  if (senha.length < 6) msgs.push('A senha deve ter pelo menos 6 caracteres')
  if (!/[a-zA-Z]/.test(senha)) msgs.push('A senha deve incluir pelo menos uma letra')
  if (!/\d/.test(senha)) msgs.push('A senha deve incluir pelo menos um número')
  if (!/[^a-zA-Z0-9]/.test(senha)) msgs.push('A senha deve incluir pelo menos um caractere especial')
  passwordAlerts.value = msgs
  passwordError.value = msgs.length ? 'obrigatório' : ''
  // Valida confirmação também ao mudar senha
  if (form.value.confirm_password && senha !== form.value.confirm_password) {
    confirmPasswordError.value = 'não coincidem.'
    errors.value.password = 'não coincidem'
  } else {
    confirmPasswordError.value = ''
    if (errors.value.password === 'coincidem') {
      errors.value.password = ''
    }
  }
})

watch(() => form.value.confirm_password, (conf) => {
  if (conf !== form.value.password) {
    confirmPasswordError.value = 'não coincidem.'
    errors.value.password = 'não coincidem'
  } else {
    confirmPasswordError.value = ''
    if (errors.value.password === 'não coincidem') {
      errors.value.password = ''
    }
  }
})


</script>