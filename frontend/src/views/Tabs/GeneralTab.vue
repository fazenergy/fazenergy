<template>
  <div class="space-y-3">
    <!-- Identidade Visual -->
    <div class="p-3 bg-white rounded">
      <h3 class="text-sm font-semibold mb-3">Identidade da Empresa</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="md:col-span-1">
          <label class="text-xs text-gray-500">Logotipo (recomendado 240x240)</label>
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
        </div>
        <div class="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-3">
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
        </div>
      </div>
      <p class="mt-2 text-[11px] text-gray-500">Observação: estes dados são apenas visuais por enquanto (sem persistência no servidor).</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({ company_name: '', cnpj: '', phone: '' })
const logoPreview = ref(null)

function onLogoChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  logoPreview.value = URL.createObjectURL(f)
}

function clearLogo() {
  logoPreview.value = null
}
</script>


