<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-left mb-4">Pré-cadastro de Afiliado</h2>
    <div v-if="!referrerValid" class="text-red-500 text-center mb-4">
      {{ referrerError }}
    </div>
    <form @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-6 gap-4">

      <!-- Linha 1 -->
      <FormField label="Indicado por" class="md:col-span-2" v-if="!isSuperUser">
        <Input v-model="form.referrer" :readonly="!!props.referrerUsername" class="bg-gray-100 text-sm" />
      </FormField>
      <FormField label="Nome Completo" :class="isSuperUser ? 'md:col-span-6' : 'md:col-span-4'">
        <Input v-model="form.full_name" placeholder="Seu nome completo" required class="text-sm" />
      </FormField>

      <!-- Linha 2 -->
      <FormField label="Email" class="md:col-span-2">
        <Input v-model="form.email" type="email" required class="text-sm" />
      </FormField>
      <FormField label="Usuário" class="md:col-span-2">
        <Input v-model="form.username" required class="text-sm" />
      </FormField>
      <FormField label="Senha" class="md:col-span-1">
        <InputPass v-model="form.password" required />
        <span
          class="block min-h-[18px] text-xs text-red-500 transition-all"
          :style="{ visibility: passwordError ? 'visible' : 'hidden' }"
        >
          {{ passwordError || ' ' }}
        </span>
      </FormField>
      <FormField label="Confirmar Senha" class="md:col-span-1">
        <InputPass v-model="form.confirm_password" required />
        <span
          class="block min-h-[18px] text-xs text-red-500 transition-all"
          :style="{ visibility: confirmPasswordError ? 'visible' : 'hidden' }"
        >
          {{ confirmPasswordError || ' ' }}
        </span>
      </FormField>

      <!-- Linha 3 -->
      <FormField label="Telefone" class="md:col-span-2">
        <Input v-model="form.phone" mask="(##) #####-####" placeholder="(00) 00000-0000" class="text-sm" />
      </FormField>
      <FormField label="Tipo de Pessoa" class="md:col-span-2">
        <Select v-model="form.person_type" required class="text-sm">
          <option disabled value="">Selecione</option>
          <option value="pf">Pessoa Física</option>
          <option value="pj">Pessoa Jurídica</option>
        </Select>
      </FormField>
      <FormField label="CPF / CNPJ" class="md:col-span-2">
        <Input v-model="form.cpfCnpj" v-mask="['###.###.###-##', '##.###.###/####-##']" placeholder="000.000.000-00" class="text-sm" />
      </FormField>

      <!-- Linha 4 -->
      <FormField label="CEP" class="md:col-span-1">
        <Input
          v-model="form.cep"
          mask="#####-###"
          placeholder="00000-000"
          class="text-sm"
          @input="fetchAddress"
        />
      </FormField>
      <FormField label="Estado" class="md:col-span-1">
      <Select v-model="form.state" required class="text-sm">
        <option disabled value="">Selecione</option>
        <option v-for="estado in estados" :key="estado.id" :value="String(estado.id)">
          {{ estado.uf }}
        </option>
      </Select>
    </FormField>
    <FormField label="Cidade" class="md:col-span-2">
     <Select v-model="form.city" required class="text-sm">
      <option disabled value="">Selecione a Cidade</option>
      <option v-for="cidade in cidades" :key="cidade.id" :value="String(cidade.id)">
        {{ cidade.name }}
      </option>
    </Select>
    </FormField>
      <FormField label="Bairro" class="md:col-span-2">
        <Input v-model="form.district" class="text-sm" />
      </FormField>

      <!-- Linha 5 -->
      <FormField label="Endereço" class="md:col-span-3">
        <Input v-model="form.address" class="text-sm" />
      </FormField>
      <FormField label="Número" class="md:col-span-1">
        <Input v-model="form.number" class="text-sm" />
      </FormField>
      <FormField label="Complemento" class="md:col-span-2">
        <Input v-model="form.complement" class="text-sm" />
      </FormField>

      <!-- Linha 6 -->
      <FormField label="Plano" class="md:col-span-4">
        <Select v-model="form.plan" class="text-sm" required>
          <option disabled value="">Selecione o Plano</option>
          <option v-for="plan in plans" :key="plan.id" :value="plan.id">{{ plan.name }}</option>
        </Select>
      </FormField>
      <div class="flex items-center md:col-span-2">
        <Checkbox v-model="form.accept_lgpd" />
        <span class="ml-2 text-sm">Li e aceito a <a href="#"> política de privacidade </a> </span>
      </div>

      <!-- Switch Raiz e Botão -->
      <div class="flex items-center md:col-span-6" v-if="isSuperUser">
        <Switch v-model="form.is_root" />
        <span class="ml-2">Indicador raiz</span>
      </div>
      <Button type="submit" class="md:col-span-6 w-full">Cadastrar</Button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import api from '@/services/axios'

// COMPONENTES
import Input from '@/components/ui/Input.vue'
import InputPass from '@/components/ui/InputPass.vue'
import Select from '@/components/ui/select.vue'
import Button from '@/components/ui/button.vue'
import Switch from '@/components/ui/switch.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import FormField from '@/components/ui/formField.vue'

// PROP
const props = defineProps({
  referrerUsername: {
    type: String,
    default: ''
  }
})

// AUTH
const auth = useAuthStore()
const isSuperUser = computed(() => auth.user?.is_superuser)
const isAuthenticated = computed(() => !!auth.user)

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
const referrerValid = ref(true)
const referrerError = ref('')

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

onMounted(async () => {
  try {
    const res = await api.get('/api/plans/plans/')
    plans.value = res.data
  } catch (err) {
    plans.value = []
  }

  // ✅ Se visitante, valida username do indicador
  if (props.referrerUsername && !isAuthenticated.value) {
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

  // Carrega estados
  const resEstados = await api.get('/api/location/states/')
  estados.value = resEstados.data

  // só usar em caso do form já ter que vier preenchido
  // if (form.value.state) {
  //   await onEstadoChange();
  // }
});
// Preenchimento automatico conforme CEP informado
async function fetchAddress() {
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
        const cidadeEncontrada = cidades.value.find(
          c => c.name.toLowerCase() === (res.localidade || '').toLowerCase()
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
}




const estados = ref([])
const cidades = ref([])

async function onEstadoChange() {
  if (form.value.state) {
    const resCidades = await api.get(`/api/location/cities/?state=${form.value.state}`);
    cidades.value = resCidades.data;
    // Limpa cidade selecionada se não existir mais
    if (!cidades.value.find(c => c.id === form.value.city)) {
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
  if (!referrerValid.value) return;
  if (passwordError.value || confirmPasswordError.value) return;

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
    await api.post('/api/users/pre-register/', payload);
    alert('Pré-cadastro realizado com sucesso!');
  } catch (error) {
    alert('Erro ao cadastrar. Verifique os dados e tente novamente.');
  }
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
  if (!isSenhaSegura(senha)) {
    passwordError.value = 'A senha deve ter ao menos 6 caracteres, incluir letra, número e caractere especial.'
  } else {
    passwordError.value = ''
  }
  // Valida confirmação também ao mudar senha
  if (form.value.confirm_password && senha !== form.value.confirm_password) {
    confirmPasswordError.value = 'As senhas não coincidem.'
  } else {
    confirmPasswordError.value = ''
  }
})

watch(() => form.value.confirm_password, (conf) => {
  if (conf !== form.value.password) {
    confirmPasswordError.value = 'As senhas não coincidem.'
  } else {
    confirmPasswordError.value = ''
  }
})


</script>