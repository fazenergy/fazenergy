<template>
  <div class="max-w-5xl mx-auto bg-white rounded-xl shadow p-8 space-y-6">
    <h2 class="text-2xl font-bold text-center mb-4">Pré-cadastro de Afiliado</h2>

    <form @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-3 gap-4">

      <!-- Indicado por -->
      <FormField label="Indicado por" class="md:col-span-3" v-if="!isSuperUser">
        <Input :value="currentUser" readonly class="bg-gray-100 text-sm" />
      </FormField>

      <!-- Indicado por -->
      <FormField label="Username do Indicador:" class="md:col-span-3" v-if="isSuperUser">
        <Input :value="currentUser" class="text-sm" />
      </FormField>

      <!-- Username -->
      <FormField label="Usuário">
        <Input v-model="form.username" placeholder="Seu usuário" required class="text-sm" />
      </FormField>

      <!-- E-mail -->
      <FormField label="Email">
        <Input v-model="form.email" type="email" placeholder="seu@email.com" required class="text-sm" />
      </FormField>

      <!-- Telefone -->
      <FormField label="Telefone">
      <Input 
        v-model="form.phone"
        placeholder="(XX) XXXXX-XXXX"
        class="text-sm"
      />
    </FormField>

      <!-- Senha -->
      <FormField label="Senha">
        <Input v-model="form.password" type="password" placeholder="********" required class="text-sm" />
      </FormField>

      <!-- Confirmar senha -->
      <FormField label="Confirmar Senha">
        <Input v-model="form.confirm_password" type="password" placeholder="********" required class="text-sm" />
      </FormField>

      <!-- Tipo de pessoa -->
      <FormField label="Tipo de Pessoa">
        <Select v-model="form.person_type" required class="text-sm">
          <option disabled value="">Selecione</option>
          <option value="pf">Pessoa Física</option>
          <option value="pj">Pessoa Jurídica</option>
        </Select>
      </FormField>

      <!-- CPF / CNPJ -->
      <FormField label="CPF / CNPJ">
  <Input 
    v-model="form.cpf_cnpj"
    placeholder="CPF ou CNPJ"
    class="text-sm"
  />
</FormField>

      <!-- CEP -->
      <FormField label="CEP">
  <Input 
    v-model="form.cep"
    placeholder="00000-000"
    @blur="fetchAddress"
    class="text-sm"
  />
</FormField>


      <!-- Número -->
      <FormField label="Número">
        <Input v-model="form.number" class="text-sm" />
      </FormField>

      <!-- Complemento -->
      <FormField label="Complemento">
        <Input v-model="form.complement" class="text-sm" />
      </FormField>

      <!-- Bairro -->
      <FormField label="Bairro">
        <Input v-model="form.district" class="text-sm" />
      </FormField>

      <!-- Plano -->
      <FormField label="Plano">
        <Select v-model="form.plan" required class="text-sm">
          <option disabled value="">Selecione o Plano</option>
          <option v-for="plan in plans" :key="plan.id" :value="plan.id">{{ plan.name }}</option>
        </Select>
      </FormField>

      <!-- Endereço -->
      <div class="md:col-span-3">
        <FormField label="Endereço">
          <Textarea v-model="form.address" rows="2" class="text-sm" />
        </FormField>
      </div>

      <!-- Aceite LGPD -->
      <div class="flex items-center md:col-span-3">
        <Checkbox v-model="form.accept_lgpd" />
        <span class="ml-2 text-sm">Li e aceito a política de privacidade</span>
      </div>

      <!-- Indicador raiz -->
      <div class="flex items-center md:col-span-3" v-if="isSuperUser">
        <Switch v-model="form.is_root" />
        <span class="ml-2">Indicador raiz</span>
      </div>

      <!-- Botão -->
      <Button type="submit" class="md:col-span-3 w-full">Cadastrar</Button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/select.vue'
import Textarea from '@/components/ui/textarea.vue'
import Button from '@/components/ui/button.vue'
import Switch from '@/components/ui/switch.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import FormField from '@/components/ui/formField.vue'
import api from '@/services/axios'



const auth = useAuthStore()
const currentUser = auth.user?.username || ''
const isSuperUser = computed(() => auth.user?.is_superuser)

const form = ref({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  person_type: '',
  cpf_cnpj: '',
  cep: '',
  phone: '',
  address: '',
  number: '',
  complement: '',
  district: '',
  plan: '',
  is_root: false,
  accept_lgpd: false,
})

const plans = ref([])

onMounted(async () => {
  const res = await api.get('/api/plans/plans/')
  plans.value = res.data
})

async function fetchAddress() {
  if (form.value.cep.replace('-', '').length === 8) {
    const res = await fetch(`https://viacep.com.br/ws/${form.value.cep}/json/`).then(r => r.json())
    if (!res.erro) {
      form.value.address = `${res.logradouro} ${res.complemento || ''}`.trim()
      form.value.district = res.bairro
    } else {
      alert('CEP não encontrado!')
    }
  }
}

function handleSubmit() {
  if (form.value.password !== form.value.confirm_password) {
    alert('Senhas não coincidem!')
    return
  }
  console.log('Dados enviados:', form.value)
}
</script>
