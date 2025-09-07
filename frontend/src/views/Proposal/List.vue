<template>
  <div class="mb-3 bg-white rounded">
    <div class="flex items-center gap-2 flex-wrap">
      <button @click="openNewModal" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <Plus class="w-4 h-4" />
        <span>Adicionar</span>
      </button>
      <button @click="exportExcel" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <FileDown class="w-4 h-4" />
        <span>Exportar</span>
      </button>
      <button @click="printGrid" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white shadow-sm inline-flex items-center gap-1.5">
        <Printer class="w-4 h-4" />
        <span>Imprimir</span>
      </button>

      <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
        <input v-model.trim="search" type="text" placeholder="Pesquisar..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
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
    <DataTable :columns="columns" :rows="filteredRows" :loading="loading" :min-height="gridMinHeight">
      <template #title>Propostas</template>
      <template #col:id="{ row }">{{ row.id }}</template>
      <template #col:cliente="{ row }">{{ row.customer_name || row.customer?.name || '-' }}</template>
      <template #col:cidade="{ row }">{{ row.city_lookup?.name || row.city_name || '-' }}</template>
      <template #col:produto="{ row }">{{ row.product?.name || '-' }}</template>
      <template #col:status="{ row }">{{ row.status || '-' }}</template>
      <template #col:created="{ row }">{{ formatDate(row.dtt_record || row.created_at) }}</template>
      <template #col:actions="{ row }">
        <div class="flex items-center gap-1">
          <button @click="viewProposal(row)" class="p-1 text-blue-600 hover:text-blue-800" title="Ver Proposta">
            <Eye class="w-4 h-4" />
          </button>
          <button @click="editProposal(row)" class="p-1 text-emerald-600 hover:text-emerald-800" title="Editar Proposta">
            <Edit class="w-4 h-4" />
          </button>
        </div>
      </template>
    </DataTable>
  </div>

  <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
    <template #title>{{ editingProposal ? 'Editar Proposta' : 'Nova Proposta' }}</template>
    <div class="p-2 text-sm text-gray-800">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-3">
        <div v-if="loadingProviders" class="md:col-span-6 text-blue-700 text-xs inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
          Buscando distribuidoras...
        </div>
        <!-- Bloco inicial + botão agrupados para garantir duas linhas -->
        <div class="md:col-span-12 grid grid-cols-12 gap-3">
          <div class="md:col-span-10">
            <div class="grid grid-cols-1 md:grid-cols-8 gap-3">
            <div class="md:col-span-2" v-if="isSuperUser">
              <label class="text-xs text-gray-600">ID do Licenciado</label>
              <input v-model.trim="form.licensed_id" type="number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Ex.: 4" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">CEP Instalação</label>
              <input v-model.trim="form.zip_code" @input="onZipInput" class="w-full border rounded px-2 py-1 text-sm" placeholder="Somente números" />
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Tipo de Imóvel</label>
              <select v-model="form.property_type" class="w-full border rounded px-2 py-1 text-sm">
                <option value="">Selecione</option>
                <option>Casa</option>
                <option>Apartamento</option>
                <option>Comercial</option>
                <option>Rural</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">Pessoa</label>
              <select v-model="form.contract_person" @change="resetValidation" class="w-full border rounded px-2 py-1 text-sm">
                <option value="PF">PF</option>
                <option value="PJ">PJ</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label class="text-xs text-gray-600">CPF/CNPJ</label>
              <input v-model.trim="form.fiscal_number" @input="resetValidation" class="w-full border rounded px-2 py-1 text-sm" />
            </div>

            <!-- Linha de baixo (aparece após validação) -->
            <div class="md:col-span-2" v-if="validatedStep">
              <label class="text-xs text-gray-600">Proprietário do Imóvel</label>
              <select v-model="form.owner" class="w-full border rounded px-2 py-1 text-sm">
                <option value="">Selecione</option>
                <option>Próprio</option>
                <option>Outro</option>
              </select>
            </div>
            <div class="md:col-span-2" v-if="validatedStep">
              <label class="text-xs text-gray-600">Distribuidora</label>
              <select v-model="form.energy_provider_id" @change="onProviderChange" class="w-full border rounded px-2 py-1 text-sm">
                <option value="">Selecione</option>
                <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div class="md:col-span-2" v-if="validatedStep">
              <label class="text-xs text-gray-600">Unidade Consumidora</label>
              <input v-model.trim="form.consumer_unit" class="w-full border rounded px-2 py-1 text-sm" />
            </div>
            <div class="md:col-span-2" v-if="validatedStep">
              <label class="text-xs text-gray-600">Grupo de Consumo</label>
              <input v-model.trim="form.consumer_group" class="w-full border rounded px-2 py-1 text-sm" placeholder="Ex.: B1, A4" />
            </div>
          </div>
          </div>
          <div class="md:col-span-2 md:row-span-2 flex items-center justify-end">
            <button type="button" @click="validateInitial" class="ml-auto px-4 py-2 h-20 w-full md:w-auto flex items-center justify-center rounded bg-blue-600 hover:bg-blue-700 text-white text-sm" :disabled="loadingProviders">
              {{ loadingProviders ? 'Validando...' : 'Validar e carregar distribuidora' }}
            </button>
          </div>
        </div>
        

        <div class="md:col-span-6" v-if="validatedStep">
          <label class="text-xs text-gray-600">Visita 1</label>
          <input v-model.trim="form.visit_1" type="datetime-local" class="w-full border rounded px-2 py-1 text-sm" />
        </div>
        <div class="md:col-span-6" v-if="validatedStep">
          <label class="text-xs text-gray-600">Visita 2</label>
          <input v-model.trim="form.visit_2" type="datetime-local" class="w-full border rounded px-2 py-1 text-sm" />
        </div>

        <!-- Consumo Mensal (linha inteira) -->
        <div v-if="validatedStep" class="md:col-span-12">
          <div class="font-semibold text-gray-700 mb-2">Consumo Mensal (kWh)</div>
          <div class="grid grid-cols-2 md:grid-cols-6 gap-3">
            <div v-for="m in months" :key="m.key">
              <label class="text-[10px] text-gray-600">{{ m.label }}</label>
              <input v-model.number="form.monthly_consumption[m.key]" type="number" min="0" class="w-full border rounded px-2 py-1 text-sm" />
            </div>
          </div>
        </div>

        <!-- Atores (abaixo do consumo) -->
        <div v-if="validatedStep" class="md:col-span-12 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <div class="font-semibold text-gray-700 mb-1">Contratante</div>
            <div class="grid grid-cols-1 gap-2">
              <input v-if="form.contract_person==='PJ'" v-model.trim="actors.contractor.legal_name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Razão Social (PJ)" />
              <input v-model.trim="actors.contractor.name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Nome" />
              <input v-model.trim="actors.contractor.cellphone" class="w-full border rounded px-2 py-1 text-sm" placeholder="Celular" />
              <input v-model.trim="actors.contractor.email" type="email" class="w-full border rounded px-2 py-1 text-sm" placeholder="E-mail" />
              <input v-model.trim="actors.contractor.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="CEP" />
              <input v-model.trim="actors.contractor.address" class="w-full border rounded px-2 py-1 text-sm" placeholder="Endereço" />
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.contractor.number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Número" />
                <input v-model.trim="actors.contractor.neighborhood" class="w-full border rounded px-2 py-1 text-sm" placeholder="Bairro" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.contractor.city" class="w-full border rounded px-2 py-1 text-sm" placeholder="Cidade" />
                <input v-model.trim="actors.contractor.st" class="w-full border rounded px-2 py-1 text-sm" placeholder="UF" />
              </div>
            </div>
          </div>

          <div v-if="form.owner==='Outro'">
            <div class="font-semibold text-gray-700 mb-1">Proprietário</div>
            <div class="grid grid-cols-1 gap-2">
              <input v-model.trim="actors.owner.name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Nome" />
              <input v-model.trim="actors.owner.cellphone" class="w-full border rounded px-2 py-1 text-sm" placeholder="Celular" />
              <input v-model.trim="actors.owner.email" type="email" class="w-full border rounded px-2 py-1 text-sm" placeholder="E-mail" />
              <input v-model.trim="actors.owner.cpf" class="w-full border rounded px-2 py-1 text-sm" placeholder="CPF" />
              <input v-model.trim="actors.owner.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="CEP" />
              <input v-model.trim="actors.owner.address" class="w-full border rounded px-2 py-1 text-sm" placeholder="Endereço" />
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.owner.number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Número" />
                <input v-model.trim="actors.owner.neighborhood" class="w-full border rounded px-2 py-1 text-sm" placeholder="Bairro" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.owner.city" class="w-full border rounded px-2 py-1 text-sm" placeholder="Cidade" />
                <input v-model.trim="actors.owner.st" class="w-full border rounded px-2 py-1 text-sm" placeholder="UF" />
              </div>
            </div>
          </div>

          <div v-if="form.contract_person==='PJ'">
            <div class="font-semibold text-gray-700 mb-1">Responsável Legal (PJ)</div>
            <div class="grid grid-cols-1 gap-2">
              <input v-model.trim="actors.legal_responsible.name" class="w-full border rounded px-2 py-1 text-sm" placeholder="Nome (obrigatório)" />
              <input v-model.trim="actors.legal_responsible.cellphone" class="w-full border rounded px-2 py-1 text-sm" placeholder="Celular" />
              <input v-model.trim="actors.legal_responsible.email" type="email" class="w-full border rounded px-2 py-1 text-sm" placeholder="E-mail" />
              <input v-model.trim="actors.legal_responsible.cpf" class="w-full border rounded px-2 py-1 text-sm" placeholder="CPF" />
              <input v-model.trim="actors.legal_responsible.zip_code" class="w-full border rounded px-2 py-1 text-sm" placeholder="CEP" />
              <input v-model.trim="actors.legal_responsible.address" class="w-full border rounded px-2 py-1 text-sm" placeholder="Endereço" />
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.legal_responsible.number" class="w-full border rounded px-2 py-1 text-sm" placeholder="Número" />
                <input v-model.trim="actors.legal_responsible.neighborhood" class="w-full border rounded px-2 py-1 text-sm" placeholder="Bairro" />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <input v-model.trim="actors.legal_responsible.city" class="w-full border rounded px-2 py-1 text-sm" placeholder="Cidade" />
                <input v-model.trim="actors.legal_responsible.st" class="w-full border rounded px-2 py-1 text-sm" placeholder="UF" />
              </div>
            </div>
          </div>
        </div>

        <div v-if="errorMsg" class="md:col-span-6 text-red-600 text-xs">{{ errorMsg }}</div>
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button @click="showNew=false" class="px-4 py-2 rounded border">Fechar</button>
        <button @click="submitProposal" :disabled="saving" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">
          {{ saving ? 'Gravando...' : (editingProposal ? 'Atualizar' : 'Gravar') }}
        </button>
      </div>
    </template>
  </Modal>

  <!-- Modal Resultado da Simulação -->
  <Modal v-model="showResult" :header-blue="true" :no-header-border="true">
    <template #title>Resultado da Simulação</template>
    <div v-if="lastResponse?.revo?.data" class="p-3 text-sm">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <!-- Bloco contrato e custos -->
        <div class="p-4 rounded border bg-white">
          <div class="text-[11px] text-gray-600">PLANO</div>
          <div class="text-lg font-extrabold">{{ lastResponse.revo.data.contract_type?.toUpperCase() }} {{ lastResponse.revo.data.contract_duration }} ANOS</div>
          <div class="mt-3 grid grid-cols-2 gap-3">
            <div>
              <div class="text-[11px] text-gray-600">Conta de luz</div>
              <div class="font-semibold">{{ fmtMoney(lastResponse.revo.data.energy_provider_costs) }}</div>
            </div>
            <div>
              <div class="text-[11px] text-gray-600">Parcela REVO</div>
              <div class="font-semibold">{{ fmtMoney(lastResponse.revo.data.energy_revo_costs) }}</div>
            </div>
          </div>
        </div>

        <!-- Bloco economia -->
        <div class="p-4 rounded border bg-white">
          <div class="text-[11px] text-gray-600">ECONOMIA ESPERADA</div>
          <div class="text-xs text-gray-600">30 ANOS</div>
          <div class="text-2xl font-extrabold text-emerald-700">{{ fmtMoney(lastResponse.revo.data.economy_thirty_years) }}</div>
          <div class="mt-2 text-[11px] text-gray-600">DESCONTO</div>
          <div class="text-xl font-bold">{{ fmtPct(lastResponse.revo.data.discount_percentage) }}</div>
        </div>

        <!-- Bloco meta -->
        <div class="p-4 rounded border bg-white">
          <div class="text-[11px] text-gray-600">PROPOSTA</div>
          <div class="text-sm">Ref.: <b>{{ lastResponse.revo.data.reference }}</b></div>
          <div class="text-sm">Validade: {{ new Date(lastResponse.revo.data.proposal_expiration_date).toLocaleDateString('pt-BR') }}</div>
          <div class="mt-2 text-[11px] text-gray-600">Distribuidora</div>
          <div class="text-sm font-medium">{{ lastResponse.revo.data.energy_provider_name }}</div>
        </div>
      </div>

      <!-- Métricas técnicas -->
      <div class="mt-4 grid grid-cols-2 md:grid-cols-6 gap-3">
        <div class="rounded border p-3 bg-white"><div class="text-[11px] text-gray-600">kWp</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.kwp) }}</div></div>
        <div class="rounded border p-3 bg-white"><div class="text-[11px] text-gray-600">kWh anual</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.kWh_annual) }}</div></div>
        <div class="rounded border p-3 bg-white"><div class="text-[11px] text-gray-600">Área (m²)</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.required_area) }}</div></div>
        <div class="rounded border p-3 bg-white"><div class="text-[11px] text-gray-600">Módulos</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.quantity_modules) }}</div></div>
        <div class="rounded border p-3 bg-white"><div class="text-[11px] text-gray-600">UC</div><div class="font-semibold">{{ lastResponse.revo.data.electric_bill?.consumer_unit || '-' }}</div></div>
        <div class="rounded border p-3 bg-white"><div class="text-[11px] text-gray-600">Grupo</div><div class="font-semibold">{{ lastResponse.revo.data.electric_bill?.consumer_group || '-' }}</div></div>
      </div>

      <!-- Planos disponíveis -->
      <div class="mt-4">
        <div class="text-xs text-gray-600 mb-1">Planos disponíveis</div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <label v-for="op in (lastResponse.revo.data.option_plans||[])" :key="op.contract_duration" class="border rounded p-3 bg-white cursor-pointer flex items-start gap-3">
            <input type="radio" class="mt-1" name="planDuration" :value="op.contract_duration" v-model="selectedDuration" />
            <div>
              <div class="font-semibold">{{ op.contract_duration }} anos</div>
              <div class="text-[11px] text-gray-600">Desconto</div>
              <div class="font-medium">{{ fmtPct(op.discount_percentage) }}</div>
              <div class="text-[11px] text-gray-600">Parcela</div>
              <div class="font-medium">{{ fmtMoney(op.energy_revo_costs) }}</div>
            </div>
          </label>
        </div>
        <div class="mt-3 flex items-center justify-end">
          <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50" :disabled="!selectedDuration" @click="openEffectiveModal">Efetivar Proposta</button>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-between gap-2">
        <div class="text-xs text-gray-600">Referência: <b>{{ lastResponse?.revo?.data?.reference }}</b></div>
        <div class="flex items-center gap-2">
          <button class="px-4 py-2 rounded border" @click="printResult">Imprimir</button>
          <button class="px-4 py-2 rounded border" @click="showResult=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white" @click="openResendModal">Reenviar Proposta</button>
        </div>
      </div>
    </template>
  </Modal>

  <!-- Modal Efetivar Proposta (PUT com plano escolhido) -->
  <Modal v-model="showEffective" :header-blue="true" :no-header-border="true">
    <template #title>Efetivar Proposta</template>
    <div class="p-3 text-sm grid grid-cols-1 md:grid-cols-2 gap-3">
      <div>
        <label class="text-xs text-gray-600">Referência</label>
        <input v-model.trim="effective.reference" class="w-full border rounded px-2 py-1 text-sm" disabled />
      </div>
      <div>
        <label class="text-xs text-gray-600">Duração do Contrato (anos)</label>
        <select v-model.number="effective.contract_duration" class="w-full border rounded px-2 py-1 text-sm">
          <option v-for="op in (lastResponse?.revo?.data?.option_plans||[])" :key="op.contract_duration" :value="op.contract_duration">{{ op.contract_duration }}</option>
        </select>
      </div>
      <div>
        <label class="text-xs text-gray-600">Unidade Consumidora</label>
        <input v-model.trim="effective.consumer_unit" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Grupo de Consumo</label>
        <input v-model.trim="effective.consumer_group" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Proprietário do Imóvel</label>
        <select v-model="effective.owner" class="w-full border rounded px-2 py-1 text-sm">
          <option>Próprio</option>
          <option>Outro</option>
        </select>
      </div>
      <div>
        <label class="text-xs text-gray-600">Celular (contratante)</label>
        <input v-model.trim="effective.cellphone" class="w-full border rounded px-2 py-1 text-sm" />
      </div>

      <div class="md:col-span-2 font-semibold text-gray-700 mt-2">Endereço de Instalação (usa o mesmo do contratante)</div>
      <div>
        <label class="text-xs text-gray-600">Endereço</label>
        <input v-model.trim="effective.installation_address.address" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Número</label>
        <input v-model.trim="effective.installation_address.number" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Complemento</label>
        <input v-model.trim="effective.installation_address.complement" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Bairro</label>
        <input v-model.trim="effective.installation_address.neighborhood" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Cidade</label>
        <input v-model.trim="effective.installation_address.city" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">UF</label>
        <input v-model.trim="effective.installation_address.st" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button class="px-4 py-2 rounded border" @click="showEffective=false">Cancelar</button>
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white" @click="submitEffective">Confirmar Efetivação</button>
      </div>
    </template>
  </Modal>
  <!-- Modal Reenviar Proposta (PUT) -->
  <Modal v-model="showResend" :header-blue="true" :no-header-border="true">
    <template #title>Reenviar Proposta</template>
    <div class="p-3 text-sm grid grid-cols-1 md:grid-cols-2 gap-3">
      <div>
        <label class="text-xs text-gray-600">Referência</label>
        <input v-model.trim="resend.reference" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Tipo de Imóvel</label>
        <input v-model.trim="resend.property_type" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Conta de Luz (R$)</label>
        <input v-model.number="resend.electric_bill" type="number" step="0.01" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
      <div>
        <label class="text-xs text-gray-600">Distribuidora ID</label>
        <input v-model.number="resend.energy_provider_id" type="number" class="w-full border rounded px-2 py-1 text-sm" />
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button class="px-4 py-2 rounded border" @click="showResend=false">Fechar</button>
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white" @click="submitResend">Reenviar</button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import DataTable from '@/components/ui/DataTable.vue'
import Modal from '@/components/ui/Modal.vue'
import api from '@/services/axios'
import { Plus, FileDown, Printer, Search, Eraser, Eye, Edit } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)
const search = ref('')
const auth = useAuthStore()
const isSuperUser = computed(() => auth.user?.is_superuser === true)

// Form state
const form = ref({
  licensed_id: '',
  zip_code: '',
  property_type: '',
  owner: '',
  energy_provider_id: '',
  energy_provider_name: '',
  consumer_unit: '',
  consumer_group: '',
  contract_person: 'PF',
  fiscal_number: '',
  seller_email: '',
  visit_1: '',
  visit_2: '',
  monthly_consumption: {
    january: 0, february: 0, march: 0, april: 0, may: 0, june: 0,
    july: 0, august: 0, september: 0, october: 0, november: 0, december: 0
  }
})
const months = [
  { key: 'january', label: 'Jan' }, { key: 'february', label: 'Fev' },
  { key: 'march', label: 'Mar' }, { key: 'april', label: 'Abr' },
  { key: 'may', label: 'Mai' }, { key: 'june', label: 'Jun' },
  { key: 'july', label: 'Jul' }, { key: 'august', label: 'Ago' },
  { key: 'september', label: 'Set' }, { key: 'october', label: 'Out' },
  { key: 'november', label: 'Nov' }, { key: 'december', label: 'Dez' }
]
const actors = ref({
  contractor: { actor: 'contractor', legal_name: '', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
  owner: { actor: 'owner', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
  legal_responsible: { actor: 'legal_responsible', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
})
const providers = ref([])
const loadingProviders = ref(false)
const saving = ref(false)
const errorMsg = ref('')
const validatedStep = ref(false)
const showResult = ref(false)
const showResend = ref(false)
const lastResponse = ref(null)
const resend = ref({ reference: '', property_type: '', electric_bill: 0, energy_provider_id: null })
const selectedDuration = ref(null)
const showEffective = ref(false)
const effective = ref({
  reference: '',
  contract_duration: null,
  consumer_unit: '',
  consumer_group: '',
  owner: 'Próprio',
  cellphone: '',
  installation_address: { address: '', number: '', complement: '', neighborhood: '', city: '', st: '' },
})

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('pt-BR')
}
function fmtMoney(v) { return `R$ ${Number(v||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` }
function fmtPct(v) { return `${Number(v||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}%` }
function fmtNum(v) { return Number(v||0).toLocaleString('pt-BR') }

onMounted(async () => {
  try {
    loading.value = true
    const { data } = await api.get('/api/contractor/proposals/')
    rows.value = data
  } catch (e) {
    rows.value = []
  } finally {
    loading.value = false
  }
  // Prefill licensed_id se existir no perfil
  try {
    const prof = await auth.fetchProfile()
    if (prof?.licensed_id) {
      form.value.licensed_id = prof.licensed_id
    }
  } catch {}
})

const columns = [
  { key: 'id', label: 'ID' },
  { key: 'cliente', label: 'Cliente' },
  { key: 'cidade', label: 'Cidade' },
  { key: 'produto', label: 'Produto' },
  { key: 'status', label: 'Status' },
  { key: 'created', label: 'Cadastro' },
  { key: 'actions', label: 'Ações' },
]

const filteredRows = computed(() => {
  const q = (search.value || '').toLowerCase()
  return rows.value.filter(r => {
    const matchSearch = !q || [
      r.id,
      r.customer_name || r.customer?.name,
      r.city_lookup?.name || r.city_name,
      r.product?.name,
      r.status
    ].some(v => (v || '').toString().toLowerCase().includes(q))
    return matchSearch
  })
})

function applySearch() {}
function clearSearch() { search.value = '' }

function exportExcel() {
  const header = ['ID', 'Cliente', 'Cidade', 'Produto', 'Status', 'Cadastro']
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.id || '')}</td>`+
    `<td>${(r.customer_name || r.customer?.name || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.product?.name || '')}</td>`+
    `<td>${(r.status || '')}</td>`+
    `<td>${formatDate(r.dtt_record || r.created_at) || ''}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `propostas_${new Date().toISOString().slice(0,10)}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printGrid() {
  const win = window.open('', '_blank')
  const rowsHtml = filteredRows.value.map(r => (
    `<tr>`+
    `<td>${(r.id || '')}</td>`+
    `<td>${(r.customer_name || r.customer?.name || '')}</td>`+
    `<td>${(r.city_lookup?.name || r.city_name || '')}</td>`+
    `<td>${(r.product?.name || '')}</td>`+
    `<td>${(r.status || '')}</td>`+
    `<td>${formatDate(r.dtt_record || r.created_at) || ''}</td>`+
    `</tr>`
  )).join('')
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Propostas</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
    </style>
  </head><body onload="window.print()">
    <h3>Propostas</h3>
    <table>
      <thead><tr><th>ID</th><th>Cliente</th><th>Cidade</th><th>Produto</th><th>Status</th><th>Cadastro</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

const showNew = ref(false)
const editingProposal = ref(null)
function openNewModal() { 
  showNew.value = true
  editingProposal.value = null
  resetForm()
}

async function validateInitial() {
  try {
    errorMsg.value = ''
    validatedStep.value = false
    const cep = (form.value.zip_code || '').replace(/\D/g, '')
    const cpf = (form.value.fiscal_number || '').replace(/\D/g, '')
    if (!form.value.licensed_id) throw new Error('Informe o ID do Licenciado')
    if (!cep) throw new Error('Informe o CEP de instalação')
    if (!cpf) throw new Error('Informe o CPF/CNPJ')
    if (!form.value.property_type) throw new Error('Informe o tipo de imóvel')

    // Verifica existência de proposta ativa
    const { data: ex } = await api.get('/api/contractor/proposals/exists/', { params: { zip_code: cep, cpf_cnpj: cpf } })
    if (ex?.exists) {
      throw new Error('Já existe proposta ativa para este CPF/CNPJ e CEP.')
    }

    // Busca distribuidora
    await fetchProviders()

    validatedStep.value = true
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e?.message || 'Falha na validação inicial'
  }
}

function resetValidation() {
  validatedStep.value = false
  providers.value = []
  form.value.energy_provider_id = ''
  form.value.energy_provider_name = ''
}

async function fetchProviders() {
  try {
    loadingProviders.value = true
    errorMsg.value = ''
    if (!form.value.zip_code) { errorMsg.value = 'Informe o CEP para buscar a distribuidora.'; return }
    const cep = (form.value.zip_code || '').replace(/\D/g, '')
    const ptype = encodeURIComponent(form.value.property_type || '')
    const url = ptype ? `/api/contractor/revo/cep/${cep}/${ptype}/` : `/api/contractor/revo/cep/${cep}/`
    const { data } = await api.get(url)
    providers.value = Array.isArray(data?.data) ? data.data : []
    if (providers.value.length) {
      form.value.energy_provider_id = providers.value[0].id
      form.value.energy_provider_name = providers.value[0].name
    }
  } catch (e) {
    providers.value = []
    errorMsg.value = 'Falha ao buscar distribuidoras para o CEP informado.'
  } finally {
    loadingProviders.value = false
  }
}

function onProviderChange() {
  const sel = providers.value.find(p => String(p.id) === String(form.value.energy_provider_id))
  form.value.energy_provider_name = sel?.name || ''
}

function onZipInput(e) {
  const raw = (e.target.value || '').replace(/\D/g, '').slice(0, 8)
  // Formata como 99999-999 quando tiver 8 dígitos
  form.value.zip_code = raw.length > 5 ? `${raw.slice(0,5)}-${raw.slice(5)}` : raw
  resetValidation()
}

async function submitProposal() {
  try {
    saving.value = true
    errorMsg.value = ''

    // Validações mínimas
    if (!form.value.licensed_id) throw new Error('Informe o ID do Licenciado')
    if (!form.value.zip_code) throw new Error('Informe o CEP de instalação')
    if (!form.value.contract_person) throw new Error('Informe o tipo de pessoa (PF/PJ)')
    if (form.value.contract_person === 'PJ') {
      const lr = actors.value.legal_responsible
      if (!lr.name || !lr.cpf) throw new Error('Responsável legal é obrigatório para PJ (nome e CPF)')
    }

    // Valida Nome e Sobrenome do contratante
    const nameContractor = (actors.value.contractor.name || '').trim()
    if (!nameContractor || nameContractor.split(/\s+/).length < 2) {
      throw new Error('Informe nome e sobrenome do contratante')
    }
    if (form.value.contract_person === 'PJ') {
      const lrName = (actors.value.legal_responsible.name || '').trim()
      if (!lrName || lrName.split(/\s+/).length < 2) {
        throw new Error('Informe nome e sobrenome do responsável legal (PJ)')
      }
    }

    const payload = {
      licensed_id: Number(form.value.licensed_id),
      zip_code: (form.value.zip_code || '').replace(/\D/g, ''),
      property_type: form.value.property_type || null,
      owner: form.value.owner || null,
      energy_provider_id: form.value.energy_provider_id ? Number(form.value.energy_provider_id) : null,
      energy_provider_name: form.value.energy_provider_name || null,
      consumer_unit: form.value.consumer_unit || null,
      consumer_group: form.value.consumer_group || null,
      contract_person: form.value.contract_person,
      fiscal_number: (form.value.fiscal_number || '').replace(/\D/g, ''),
      // seller_email é definido no backend via REVO_SELLER_EMAIL
      visit_1: form.value.visit_1 || null,
      visit_2: form.value.visit_2 || null,
      monthly_consumption: { ...form.value.monthly_consumption },
      lead_actors: [actors.value.contractor, actors.value.owner, actors.value.legal_responsible].filter(a => a && (a.name || a.legal_name))
    }

    const { data } = await api.post('/api/contractor/revo/simulation/', payload)
    lastResponse.value = data || null
    // Atualiza a lista
    await refreshList()
    // Fecha formulário e exibe resultado
    showNew.value = false
    showResult.value = true
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e?.message || 'Erro ao salvar a proposta'
  } finally {
    saving.value = false
  }
}

async function refreshList() {
  try {
    loading.value = true
    const { data } = await api.get('/api/contractor/proposals/')
    rows.value = data
  } finally { loading.value = false }
}

function openResendModal() {
  const ref = lastResponse.value?.revo?.data?.reference || lastResponse.value?.proposal?.reference_code
  resend.value.reference = ref || ''
  resend.value.property_type = lastResponse.value?.revo?.data?.property_type || ''
  resend.value.electric_bill = Number(lastResponse.value?.revo?.data?.electric_bill?.value || 0)
  resend.value.energy_provider_id = lastResponse.value?.revo?.data?.energy_provider_id || null
  showResend.value = true
}

async function submitResend() {
  try {
    saving.value = true
    const body = {
      reference: resend.value.reference,
      property_type: resend.value.property_type || null,
      electric_bill: resend.value.electric_bill || 0,
      energy_provider_id: resend.value.energy_provider_id || null,
    }
    const { data } = await api.put('/api/contractor/revo/simulation/', body)
    lastResponse.value = data || lastResponse.value
    showResend.value = false
    showResult.value = true
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || 'Erro ao reenviar proposta')
  } finally {
    saving.value = false
  }
}

function printResult() {
  const d = lastResponse.value?.revo?.data
  if (!d) return
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
  <title>Resultado da Simulação</title>
  <style>
    body{font-family: Arial, sans-serif;}
    .card{border:1px solid #ddd;border-radius:6px;padding:12px;margin:8px 0}
    .grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
    .muted{color:#555;font-size:12px}
    .title{font-size:16px;font-weight:800}
  </style>
  </head><body onload="window.print()">
    <div class="grid">
      <div class="card"><div class="muted">PLANO</div><div class="title">${(d.contract_type||'').toUpperCase()} ${d.contract_duration} ANOS</div>
        <div class="muted">Conta de luz</div><div><b>R$ ${(Number(d.energy_provider_costs||0)).toLocaleString('pt-BR',{minimumFractionDigits:2})}</b></div>
        <div class="muted">Parcela REVO</div><div><b>R$ ${(Number(d.energy_revo_costs||0)).toLocaleString('pt-BR',{minimumFractionDigits:2})}</b></div>
      </div>
      <div class="card"><div class="muted">ECONOMIA 30 ANOS</div><div class="title">R$ ${(Number(d.economy_thirty_years||0)).toLocaleString('pt-BR',{minimumFractionDigits:2})}</div>
        <div class="muted">Desconto</div><div><b>${(Number(d.discount_percentage||0)).toLocaleString('pt-BR',{minimumFractionDigits:2})}%</b></div>
      </div>
      <div class="card"><div class="muted">PROPOSTA</div>
        <div>Ref.: <b>${d.reference||'-'}</b></div>
        <div>Validade: ${(new Date(d.proposal_expiration_date)).toLocaleDateString('pt-BR')}</div>
        <div class="muted">Distribuidora</div><div><b>${d.energy_provider_name||'-'}</b></div>
      </div>
    </div>
  </body></html>`
  const win = window.open('', '_blank')
  win.document.write(html)
  win.document.close()
}

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}
onMounted(() => {
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))

// Funções para visualizar e editar propostas
async function viewProposal(row) {
  try {
    // Busca o resultado da proposta
    const { data } = await api.get(`/api/contractor/proposal-results/?proposal=${row.id}`)
    if (data && data.length > 0) {
      const result = data[0]
      // Monta a resposta no formato esperado pelo modal de resultado
      lastResponse.value = {
        revo: {
          data: result.response_payload?.data || {
            reference: result.proposal?.reference_code,
            contract_type: result.contract_type,
            contract_duration: result.contract_duration,
            discount_percentage: result.discount_percentage,
            energy_provider_costs: result.provider_costs,
            energy_revo_costs: result.revo_costs,
            economy_thirty_years: result.economy_thirty_years,
            energy_provider_name: result.energy_provider_name,
            proposal_expiration_date: result.proposal_expiration_at,
            kwp: result.kwp,
            kWh_annual: result.kwh_annual,
            required_area: result.required_area,
            quantity_modules: result.qty_modules,
            electric_bill: {
              consumer_unit: result.consumer_unit,
              consumer_group: result.consumer_group
            }
          }
        },
        proposal: result.proposal,
        result: result
      }
      showResult.value = true
    } else {
      alert('Resultado da proposta não encontrado')
    }
  } catch (e) {
    alert('Erro ao carregar proposta: ' + (e?.response?.data?.detail || e?.message))
  }
}

function editProposal(row) {
  editingProposal.value = row
  showNew.value = true
  resetForm()
  
  // Preenche o formulário com os dados da proposta
  form.value.licensed_id = row.contractor?.licensed_id || ''
  form.value.zip_code = row.zip_code || ''
  form.value.property_type = row.property_type || ''
  form.value.owner = row.owner || ''
  form.value.energy_provider_id = row.energy_provider_id || ''
  form.value.energy_provider_name = row.energy_provider_name || ''
  form.value.consumer_unit = row.consumer_unit || ''
  form.value.consumer_group = row.consumer_group || ''
  form.value.contract_person = row.contract_person || 'PF'
  form.value.fiscal_number = row.cpf_cnpj || ''
  form.value.visit_1 = row.visit_1 || ''
  form.value.visit_2 = row.visit_2 || ''
  form.value.monthly_consumption = row.monthly_consumption || {
    january: 0, february: 0, march: 0, april: 0, may: 0, june: 0,
    july: 0, august: 0, september: 0, october: 0, november: 0, december: 0
  }
  
  // Preenche os atores (busca os lead_actors da proposta)
  // Por enquanto, deixa vazio - pode ser implementado depois se necessário
  actors.value = {
    contractor: { actor: 'contractor', legal_name: '', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
    owner: { actor: 'owner', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
    legal_responsible: { actor: 'legal_responsible', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
  }
  
  // Simula validação para mostrar campos avançados
  validatedStep.value = true
}

function resetForm() {
  form.value = {
    licensed_id: '',
    zip_code: '',
    property_type: '',
    owner: '',
    energy_provider_id: '',
    energy_provider_name: '',
    consumer_unit: '',
    consumer_group: '',
    contract_person: 'PF',
    fiscal_number: '',
    seller_email: '',
    visit_1: '',
    visit_2: '',
    monthly_consumption: {
      january: 0, february: 0, march: 0, april: 0, may: 0, june: 0,
      july: 0, august: 0, september: 0, october: 0, november: 0, december: 0
    }
  }
  actors.value = {
    contractor: { actor: 'contractor', legal_name: '', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
    owner: { actor: 'owner', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
    legal_responsible: { actor: 'legal_responsible', name: '', cellphone: '', email: '', cpf: '', zip_code: '', address: '', number: '', neighborhood: '', city: '', st: '' },
  }
  validatedStep.value = false
  providers.value = []
  errorMsg.value = ''
}

function openEffectiveModal() {
  const d = lastResponse.value?.revo?.data || {}
  selectedDuration.value = selectedDuration.value || d.contract_duration || null
  effective.value.reference = d.reference || lastResponse.value?.proposal?.reference_code || ''
  effective.value.contract_duration = Number(selectedDuration.value || d.contract_duration || 0)
  effective.value.consumer_unit = d.electric_bill?.consumer_unit || lastResponse.value?.proposal?.consumer_unit || ''
  effective.value.consumer_group = d.electric_bill?.consumer_group || lastResponse.value?.proposal?.consumer_group || ''
  effective.value.owner = lastResponse.value?.proposal?.owner || 'Próprio'
  effective.value.cellphone = actors.value.contractor.cellphone || ''
  effective.value.installation_address = {
    address: lastResponse.value?.proposal?.address || '',
    number: lastResponse.value?.proposal?.number || '',
    complement: lastResponse.value?.proposal?.complement || '',
    neighborhood: lastResponse.value?.proposal?.neighborhood || '',
    city: lastResponse.value?.proposal?.city || '',
    st: lastResponse.value?.proposal?.state || '',
  }
  showEffective.value = true
}

async function submitEffective() {
  try {
    saving.value = true
    const body = {
      reference: effective.value.reference,
      contract_duration: String(effective.value.contract_duration || ''),
      cellphone: String(effective.value.cellphone || ''),
      owner: effective.value.owner || 'Próprio',
      consumer_unit: effective.value.consumer_unit || null,
      consumer_group: effective.value.consumer_group || null,
      installation_address: { ...effective.value.installation_address },
      lead_actors: [
        {
          actor: 'contractor',
          name: actors.value.contractor.name,
          cellphone: actors.value.contractor.cellphone,
          email: actors.value.contractor.email,
          fiscal_number: form.value.fiscal_number,
          zip_code: actors.value.contractor.zip_code,
          address: actors.value.contractor.address,
          number: actors.value.contractor.number,
          complement: actors.value.contractor.complement,
          neighborhood: actors.value.contractor.neighborhood,
          city: actors.value.contractor.city,
          st: actors.value.contractor.st,
        }
      ]
    }
    const { data } = await api.put('/api/contractor/revo/simulation/', body)
    lastResponse.value = data || lastResponse.value
    showEffective.value = false
    showResult.value = true
    await refreshList()
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || 'Erro ao efetivar proposta')
  } finally {
    saving.value = false
  }
}
</script>


