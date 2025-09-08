<template>
  <div class="mb-3 bg-white rounded">
    <Toast v-model="toast.show" :message="toast.message" :type="toast.type" />

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
      <template #col:contractor_name="{ row }">{{ row.contractor?.lead_name || row.contractor?.legal_name || row.contractor?.name || '-' }}</template>
      <template #col:contractor_email="{ row }">{{ row.contractor?.email || row.email || '-' }}</template>
      <template #col:contractor_cell="{ row }">{{ row.contractor?.cellphone || '-' }}</template>
      <template #col:provider="{ row }">{{ row.energy_provider_name || '-' }}</template>
      <template #col:created="{ row }">{{ formatDate(row.dtt_record || row.created_at) }}</template>
      <template #col:expired="{ row }">{{ formatDate(row.dtt_expired) }}</template>
      <template #col:reference="{ row }">{{ row.reference_code || '-' }}</template>
      <template #col:status="{ row }">{{ row.status || '-' }}</template>
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
    <template #title>{{ editingProposal ? 'Editar Proposta' : 'Simular Proposta' }}</template>
    <div class="p-2 text-sm text-gray-800">
      <div v-if="errorMsg" class="mb-3">
        <div class="border border-red-200 bg-red-50 text-red-800 text-xs rounded px-3 py-2">{{ errorMsg }}</div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-12 gap-3">
        <div v-if="loadingProviders" class="md:col-span-6 text-blue-700 text-xs inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
          Buscando distribuidoras...
        </div>
        <!-- Bloco inicial com 5 colunas por linha e botão na primeira linha -->
        <div class="md:col-span-12">
          <div class="relative border border-slate-200 rounded-lg p-3 md:p-4 bg-white shadow-sm">
            <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-white">Dados iniciais</div>
            <div class="grid grid-cols-1 md:grid-cols-10 gap-3 mt-1">
              <div class="md:col-span-2" v-if="isSuperUser">
                <label class="text-xs text-gray-600">ID do Licenciado</label>
                <input v-model.trim="form.licensed_id" type="number" :disabled="!!editingProposal" class="w-full border rounded px-2 py-1 text-sm" placeholder="Ex.: 4" />
              </div>
              <div class="md:col-span-2">
                <label class="text-xs text-gray-600">CEP Instalação</label>
                <input v-model.trim="form.zip_code" @input="onZipInput" :disabled="!!editingProposal" class="w-full border rounded px-2 py-1 text-sm" placeholder="Somente números" />
              </div>
              <div class="md:col-span-2">
                <label class="text-xs text-gray-600">Tipo de Imóvel</label>
                <select v-model="form.property_type" :disabled="!!editingProposal" class="w-full border rounded px-2 py-1 text-sm">
                  <option value="">Selecione</option>
                  <option>Casa</option>
                  <option>Apartamento</option>
                  <option>Comercial</option>
                  <option>Rural</option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label class="text-xs text-gray-600">Pessoa</label>
                <select v-model="form.contract_person" @change="resetValidation" :disabled="!!editingProposal" class="w-full border rounded px-2 py-1 text-sm">
                  <option value="PF">PF</option>
                  <option value="PJ">PJ</option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label class="text-xs text-gray-600">CPF/CNPJ</label>
                <input v-model.trim="form.fiscal_number" @input="resetValidation" :disabled="!!editingProposal" class="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div class="md:col-span-2 flex items-end">
                <button v-if="!editingProposal" type="button" @click="validateInitial" class="px-4 py-2 h-10 w-full flex items-center justify-center rounded bg-blue-600 hover:bg-blue-700 text-white text-sm" :disabled="loadingProviders">
                  {{ loadingProviders ? 'Validando...' : 'Validar e carregar distribuidora' }}
                </button>
              </div>

              <!-- Linha de baixo (aparece após validação) -->
              <div class="md:col-span-2" v-if="validatedStep">
                <label class="text-xs text-gray-600 inline-flex items-center gap-1">Proprietário do Imóvel <span class="text-red-500">*</span></label>
                <select v-model="form.owner" :disabled="!!editingProposal" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !form.owner ? 'border-red-500' : '']">
                  <option value="">Selecione</option>
                  <option>Próprio</option>
                  <option>Outro</option>
                </select>
              </div>
              <div class="md:col-span-2" v-if="validatedStep">
                <label class="text-xs text-gray-600 inline-flex items-center gap-1">Distribuidora <span class="text-red-500">*</span></label>
                <template v-if="!editingProposal">
                  <select v-model="form.energy_provider_id" @change="onProviderChange" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !form.energy_provider_id ? 'border-red-500' : '']">
                    <option value="">Selecione</option>
                    <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>
                </template>
                <template v-else>
                  <input v-model="form.energy_provider_name" disabled class="w-full border rounded px-2 py-1 text-sm bg-gray-50" />
                </template>
              </div>
              <div class="md:col-span-2" v-if="validatedStep">
                <label class="text-xs text-gray-600 inline-flex items-center gap-1">Unidade Consumidora <span class="text-red-500">*</span></label>
                <input v-model.trim="form.consumer_unit" :disabled="!!editingProposal" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !form.consumer_unit ? 'border-red-500' : '']" />
              </div>
              <div class="md:col-span-2" v-if="validatedStep">
                <label class="text-xs text-gray-600 inline-flex items-center gap-1">Grupo de Consumo <span class="text-red-500">*</span></label>
                <input v-model.trim="form.consumer_group" :disabled="!!editingProposal" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !form.consumer_group ? 'border-red-500' : '']" placeholder="Ex.: B1, A4" />
              </div>
              <div class="md:col-span-2" v-if="validatedStep">
                <label class="text-xs text-gray-600">Valor da Última Fatura (R$)</label>
                <input v-model.number="form.electric_bill" type="number" step="0.01" min="0" :disabled="!!editingProposal" class="w-full border rounded px-2 py-1 text-sm" placeholder="0,00" />
              </div>
            </div>
          </div>
        </div>
        

        <div class="md:col-span-12" v-if="validatedStep">
          <div class="relative border border-slate-200 rounded-lg p-3 md:p-4 bg-white shadow-sm">
            <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-white">Agendamento</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-1">
              <div>
                <label class="text-xs text-gray-600">Visita 1</label>
                <input v-model.trim="form.visit_1" type="datetime-local" class="w-full border rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label class="text-xs text-gray-600">Visita 2</label>
                <input v-model.trim="form.visit_2" type="datetime-local" class="w-full border rounded px-2 py-1 text-sm" />
              </div>
            </div>
          </div>
        </div>

        <!-- Consumo Mensal (linha inteira) -->
        <div v-if="validatedStep" class="md:col-span-12">
          <div class="relative border border-slate-200 rounded-lg p-3 md:p-4 bg-slate-50 shadow-sm">
            <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-slate-50">Consumo Mensal (kWh) <span class="text-red-500">*</span></div>
            <div class="grid grid-cols-2 md:grid-cols-6 gap-3 mt-1">
              <div v-for="m in months" :key="m.key">
                <label class="text-[10px] text-gray-600">{{ m.label }}</label>
                <input v-model.number="form.monthly_consumption[m.key]" type="number" min="0" :disabled="!!editingProposal" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && isMonthMissing(m.key) ? 'border-red-500' : '']" />
              </div>
            </div>
          </div>
        </div>

        <!-- Atores (abaixo do consumo) -->
        <div v-if="validatedStep && !editingProposal" class="md:col-span-12">
          <div class="relative border border-slate-200 rounded-lg p-3 md:p-4 bg-white shadow-sm">
            <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-white">Atores</div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-1">
              <div class="border border-slate-200 rounded-lg bg-slate-50 p-3">
                <div class="text-xs font-semibold text-gray-700 mb-2">Contratante</div>
                <div class="grid grid-cols-1 gap-2">
                  <template v-if="form.contract_person==='PJ'">
                    <div>
                      <label class="text-[10px] text-gray-600">Razão Social (PJ)</label>
                      <input v-model.trim="actors.contractor.legal_name" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </template>
                  <div>
                    <label class="text-[10px] text-gray-600">Nome Completo <span class="text-red-500" v-if="!actors.contractor.name">*</span></label>
                    <input v-model.trim="actors.contractor.name" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !actors.contractor.name ? 'border-red-500' : '']" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Celular</label>
                    <input v-model.trim="actors.contractor.cellphone" @input="onPhoneInput('contractor')" maxlength="11" inputmode="numeric" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">E-mail <span class="text-red-500" v-if="!actors.contractor.email">*</span></label>
                    <input v-model.trim="actors.contractor.email" type="email" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !actors.contractor.email ? 'border-red-500' : '']" />
                  </div>
                  <template v-if="form.contract_person==='PF'">
                    <div>
                      <label class="text-[10px] text-gray-600">CPF</label>
                      <input v-model.trim="actors.contractor.cpf" @input="actors.contractor.cpf = (actors.contractor.cpf || '').toString().replace(/\D/g,'').slice(0,11)" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </template>
                  <div>
                    <label class="text-[10px] text-gray-600">CEP <span class="text-red-500" v-if="!isValidZip(actors.contractor.zip_code)">*</span></label>
                    <input v-model.trim="actors.contractor.zip_code" :class="['w-full border rounded px-2 py-1 text-sm', showFieldErrors && !isValidZip(actors.contractor.zip_code) ? 'border-red-500' : '']" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Endereço</label>
                    <input v-model.trim="actors.contractor.address" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Número</label>
                      <input v-model.trim="actors.contractor.number" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">Bairro</label>
                      <input v-model.trim="actors.contractor.neighborhood" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Cidade</label>
                      <input v-model.trim="actors.contractor.city" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">UF</label>
                      <input v-model.trim="actors.contractor.st" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="form.owner==='Outro'" class="border border-slate-200 rounded-lg bg-slate-50 p-3">
                <div class="text-xs font-semibold text-gray-700 mb-2">Proprietário</div>
                <div class="grid grid-cols-1 gap-2">
                  <div>
                    <label class="text-[10px] text-gray-600">Nome</label>
                    <input v-model.trim="actors.owner.name" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Celular</label>
                    <input v-model.trim="actors.owner.cellphone" @input="onPhoneInput('owner')" maxlength="11" inputmode="numeric" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">E-mail</label>
                    <input v-model.trim="actors.owner.email" type="email" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CPF</label>
                    <input v-model.trim="actors.owner.cpf" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CEP</label>
                    <input v-model.trim="actors.owner.zip_code" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Endereço</label>
                    <input v-model.trim="actors.owner.address" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Número</label>
                      <input v-model.trim="actors.owner.number" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">Bairro</label>
                      <input v-model.trim="actors.owner.neighborhood" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Cidade</label>
                      <input v-model.trim="actors.owner.city" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">UF</label>
                      <input v-model.trim="actors.owner.st" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="form.contract_person==='PJ'" class="border border-slate-200 rounded-lg bg-slate-50 p-3">
                <div class="text-xs font-semibold text-gray-700 mb-2">Responsável Legal (PJ)</div>
                <div class="grid grid-cols-1 gap-2">
                  <div>
                    <label class="text-[10px] text-gray-600">Nome Completo</label>
                    <input v-model.trim="actors.legal_responsible.name" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Celular</label>
                    <input v-model.trim="actors.legal_responsible.cellphone" @input="onPhoneInput('legal_responsible')" maxlength="11" inputmode="numeric" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">E-mail</label>
                    <input v-model.trim="actors.legal_responsible.email" type="email" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CPF</label>
                    <input v-model.trim="actors.legal_responsible.cpf" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CEP</label>
                    <input v-model.trim="actors.legal_responsible.zip_code" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Endereço</label>
                    <input v-model.trim="actors.legal_responsible.address" class="w-full border rounded px-2 py-1 text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Número</label>
                      <input v-model.trim="actors.legal_responsible.number" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">Bairro</label>
                      <input v-model.trim="actors.legal_responsible.neighborhood" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Cidade</label>
                      <input v-model.trim="actors.legal_responsible.city" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">UF</label>
                      <input v-model.trim="actors.legal_responsible.st" class="w-full border rounded px-2 py-1 text-sm" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Atores em modo edição: exibir como texto (somente visitas são editáveis) -->
        <div v-if="validatedStep && editingProposal" class="md:col-span-12 grid grid-cols-1 md:grid-cols-3 gap-3">
          <!-- Contratante (texto) -->
          <div>
            <div class="font-semibold text-gray-700 mb-1">Contratante</div>
            <div class="grid grid-cols-1 gap-1">
              <div>
                <div class="text-[10px] text-gray-600">Nome/Razão Social</div>
                <div class="text-sm font-medium">{{ actors.contractor.legal_name || actors.contractor.name || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">E-mail</div>
                <div class="text-sm font-medium">{{ actors.contractor.email || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">Celular</div>
                <div class="text-sm font-medium">{{ actors.contractor.cellphone || '-' }}</div>
              </div>
              <div v-if="form.contract_person==='PF'">
                <div class="text-[10px] text-gray-600">CPF</div>
                <div class="text-sm font-medium">{{ actors.contractor.cpf || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">CEP</div>
                <div class="text-sm font-medium">{{ actors.contractor.zip_code || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">Endereço</div>
                <div class="text-sm font-medium">{{ actors.contractor.address || '-' }}</div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-[10px] text-gray-600">Número</div>
                  <div class="text-sm font-medium">{{ actors.contractor.number || '-' }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-600">Bairro</div>
                  <div class="text-sm font-medium">{{ actors.contractor.neighborhood || '-' }}</div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-[10px] text-gray-600">Cidade</div>
                  <div class="text-sm font-medium">{{ actors.contractor.city || '-' }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-600">UF</div>
                  <div class="text-sm font-medium">{{ actors.contractor.st || '-' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Proprietário (texto) -->
          <div v-if="form.owner==='Outro'">
            <div class="font-semibold text-gray-700 mb-1">Proprietário</div>
            <div class="grid grid-cols-1 gap-1">
              <div>
                <div class="text-[10px] text-gray-600">Nome</div>
                <div class="text-sm font-medium">{{ actors.owner.name || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">E-mail</div>
                <div class="text-sm font-medium">{{ actors.owner.email || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">Celular</div>
                <div class="text-sm font-medium">{{ actors.owner.cellphone || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">CPF</div>
                <div class="text-sm font-medium">{{ actors.owner.cpf || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">CEP</div>
                <div class="text-sm font-medium">{{ actors.owner.zip_code || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">Endereço</div>
                <div class="text-sm font-medium">{{ actors.owner.address || '-' }}</div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-[10px] text-gray-600">Número</div>
                  <div class="text-sm font-medium">{{ actors.owner.number || '-' }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-600">Bairro</div>
                  <div class="text-sm font-medium">{{ actors.owner.neighborhood || '-' }}</div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-[10px] text-gray-600">Cidade</div>
                  <div class="text-sm font-medium">{{ actors.owner.city || '-' }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-600">UF</div>
                  <div class="text-sm font-medium">{{ actors.owner.st || '-' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Responsável Legal (texto) -->
          <div v-if="form.contract_person==='PJ'">
            <div class="font-semibold text-gray-700 mb-1">Responsável Legal (PJ)</div>
            <div class="grid grid-cols-1 gap-1">
              <div>
                <div class="text-[10px] text-gray-600">Nome</div>
                <div class="text-sm font-medium">{{ actors.legal_responsible.name || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">E-mail</div>
                <div class="text-sm font-medium">{{ actors.legal_responsible.email || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">Celular</div>
                <div class="text-sm font-medium">{{ actors.legal_responsible.cellphone || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">CPF</div>
                <div class="text-sm font-medium">{{ actors.legal_responsible.cpf || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">CEP</div>
                <div class="text-sm font-medium">{{ actors.legal_responsible.zip_code || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-600">Endereço</div>
                <div class="text-sm font-medium">{{ actors.legal_responsible.address || '-' }}</div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-[10px] text-gray-600">Número</div>
                  <div class="text-sm font-medium">{{ actors.legal_responsible.number || '-' }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-600">Bairro</div>
                  <div class="text-sm font-medium">{{ actors.legal_responsible.neighborhood || '-' }}</div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <div class="text-[10px] text-gray-600">Cidade</div>
                  <div class="text-sm font-medium">{{ actors.legal_responsible.city || '-' }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-600">UF</div>
                  <div class="text-sm font-medium">{{ actors.legal_responsible.st || '-' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        
      </div>
    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button @click="handleCloseNew()" class="px-4 py-2 rounded border">Fechar</button>
        <button @click="submitProposal" :disabled="saving || (!validatedStep && !editingProposal)" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">
          {{ editingProposal ? (saving ? 'Atualizando...' : 'Atualizar') : (saving ? 'Simulando...' : 'Simular') }}
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
        <div class="p-4 rounded-lg border border-slate-200 bg-slate-50">
          <div class="text-[11px] text-gray-600">PLANO ESCOLHIDO</div>
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
        <div class="p-4 rounded-lg border border-slate-200 bg-slate-50">
          <div class="text-[11px] text-gray-600">ECONOMIA ESPERADA</div>
          <div class="text-xs text-gray-600">30 ANOS</div>
          <div class="text-2xl font-extrabold text-emerald-700">{{ fmtMoney(lastResponse.revo.data.economy_thirty_years) }}</div>
          <div class="mt-2 text-[11px] text-gray-600">DESCONTO</div>
          <div class="text-xl font-bold">{{ fmtPct(lastResponse.revo.data.discount_percentage) }}</div>
        </div>

        <!-- Bloco meta -->
        <div class="p-4 rounded-lg border border-slate-200 bg-slate-50">
          <div class="text-[11px] text-gray-600">PROPOSTA</div>
          <div class="text-sm">Ref.: <b>{{ lastResponse.revo.data.reference }}</b></div>
          <div class="text-sm">Validade: {{ new Date(lastResponse.revo.data.proposal_expiration_date).toLocaleDateString('pt-BR') }}</div>
          <div class="mt-2 text-[11px] text-gray-600">Distribuidora</div>
          <div class="text-sm font-medium">{{ lastResponse.revo.data.energy_provider_name }}</div>
        </div>
      </div>

      <!-- Métricas técnicas -->
      <div class="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3">
        <div class="rounded-lg border border-slate-200 p-3 bg-slate-50 shadow-sm"><div class="text-[11px] text-gray-600">Última fatura</div><div class="font-semibold">{{ fmtMoney(lastResponse.revo.data.energy_provider_electric_bill || lastResponse.proposal?.electric_bill_amount) }}</div></div>
        <div class="rounded-lg border border-slate-200 p-3 bg-slate-50 shadow-sm"><div class="text-[11px] text-gray-600">kWp</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.kwp) }}</div></div>
        <div class="rounded-lg border border-slate-200 p-3 bg-slate-50 shadow-sm"><div class="text-[11px] text-gray-600">kWh anual</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.kWh_annual) }}</div></div>
        <div class="rounded-lg border border-slate-200 p-3 bg-slate-50 shadow-sm"><div class="text-[11px] text-gray-600">Área (m²)</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.required_area) }}</div></div>
        <div class="rounded-lg border border-slate-200 p-3 bg-slate-50 shadow-sm"><div class="text-[11px] text-gray-600">Módulos</div><div class="font-semibold">{{ fmtNum(lastResponse.revo.data.quantity_modules) }}</div></div>
        
      </div>

      <!-- Consumo Mensal (fieldset style) -->
      <div class="mt-4">
        <div class="relative border border-slate-200 rounded-lg p-3 bg-slate-50 shadow-sm">
          <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-slate-50 flex items-center gap-2">
            <span>Consumo mensal (kWh)</span>
            <button class="inline-flex items-center gap-1 px-2 py-0.5 rounded border border-slate-300 text-[11px] hover:bg-slate-100" @click="showMonthly = !showMonthly">
              <span>{{ showMonthly ? 'Esconder' : 'Mostrar' }}</span>
              <ChevronDown v-if="showMonthly" class="w-3.5 h-3.5" />
              <ChevronRight v-else class="w-3.5 h-3.5" />
            </button>
          </div>
          <div v-if="showMonthly" class="grid grid-cols-2 md:grid-cols-6 gap-3 mt-1">
            <div v-for="m in months" :key="'mon-'+m.key">
              <div class="text-[11px] text-gray-600">{{ m.label }}</div>
              <div class="font-medium">{{ fmtNum((lastResponse.proposal?.monthly_consumption || {})[m.key]) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Planos disponíveis (fieldset style) -->
      <div class="mt-4">
        <div class="relative border border-slate-200 rounded-lg p-3 bg-white shadow-sm">
          <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-white">Planos disponíveis</div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mt-1">
          <label
            v-for="op in (lastResponse.revo.data.option_plans||[])"
            :key="op.contract_duration"
            :class="[
              'relative border rounded p-3 bg-slate-50 cursor-pointer flex items-start gap-3 transition-colors shadow-sm',
              selectedDuration === op.contract_duration ? 'border-2 border-emerald-600 ring-2 ring-emerald-100 bg-emerald-50 shadow-md' : 'hover:border-emerald-300'
            ]"
          >
            <input type="radio" class="mt-1" name="planDuration" :value="op.contract_duration" v-model="selectedDuration" />
            <div>
              <div class="font-semibold">{{ op.contract_duration }} anos</div>
              <div class="text-[11px] text-gray-600">Desconto</div>
              <div class="font-medium">{{ fmtPct(op.discount_percentage) }}</div>
              <div class="text-[11px] text-gray-600">Parcela</div>
              <div class="font-medium">{{ fmtMoney(op.energy_revo_costs) }}</div>
            </div>
            <CheckCircle v-if="selectedDuration === op.contract_duration" class="absolute top-2 right-2 w-4 h-4 text-emerald-600" />
          </label>
          </div>
        </div>
      </div>

      <!-- Campos editáveis para efetivação -->
      <div v-if="selectedDuration" class="mt-6">
        <div class="relative border border-slate-200 rounded-lg p-3 md:p-4 bg-slate-50 shadow-sm">
          <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-slate-50">Dados para efetivação</div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label class="text-[11px] text-slate-600">Unidade Consumidora</label>
              <input v-model.trim="effective.consumer_unit" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-[11px] text-slate-600">Grupo de Consumo</label>
              <input v-model.trim="effective.consumer_group" class="w-full border rounded px-2 py-1 h-8 text-sm" />
            </div>
            <div>
              <label class="text-[11px] text-slate-600">Proprietário do Imóvel</label>
              <select v-model="effective.owner" class="w-full border rounded px-2 py-1 h-8 text-sm">
                <option>Próprio</option>
                <option>Outro</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Atores: seção própria -->
        <div class="mt-4">
          <div class="relative border border-slate-200 rounded-lg p-3 md:p-4 bg-white shadow-sm">
            <div class="absolute -top-2 left-3 px-2 text-[11px] font-medium text-slate-500 bg-white">Atores</div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-1">
              <!-- Contratante -->
              <div class="border border-slate-200 rounded-lg bg-slate-50 p-3">
                <div class="text-xs font-semibold text-gray-700 mb-2">Contratante</div>
                <div class="grid grid-cols-1 gap-2">
                  <template v-if="form.contract_person==='PJ'">
                    <div>
                      <label class="text-[10px] text-gray-600">Razão Social (PJ)</label>
                      <input v-model.trim="actors.contractor.legal_name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </template>
                  <div>
                    <label class="text-[10px] text-gray-600">Nome Completo</label>
                    <input v-model.trim="actors.contractor.name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Celular</label>
                    <input v-model.trim="actors.contractor.cellphone" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">E-mail</label>
                    <input v-model.trim="actors.contractor.email" type="email" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <template v-if="form.contract_person==='PF'">
                    <div>
                      <label class="text-[10px] text-gray-600">CPF</label>
                      <input v-model.trim="actors.contractor.cpf" disabled class="w-full border rounded px-2 py-1 h-8 text-sm bg-gray-50" />
                    </div>
                  </template>
                  <div>
                    <label class="text-[10px] text-gray-600">CEP</label>
                    <input v-model.trim="actors.contractor.zip_code" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Endereço</label>
                    <input v-model.trim="actors.contractor.address" @input="syncContractorAddressToInstallation" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Número</label>
                      <input v-model.trim="actors.contractor.number" @input="syncContractorAddressToInstallation" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">Bairro</label>
                      <input v-model.trim="actors.contractor.neighborhood" @input="syncContractorAddressToInstallation" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Cidade</label>
                      <input v-model.trim="actors.contractor.city" @input="syncContractorAddressToInstallation" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">UF</label>
                      <input v-model.trim="actors.contractor.st" @input="syncContractorAddressToInstallation" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Proprietário -->
              <div v-if="effective.owner==='Outro'" class="border border-slate-200 rounded-lg bg-slate-50 p-3">
                <div class="text-xs font-semibold text-gray-700 mb-2">Proprietário</div>
                <div class="grid grid-cols-1 gap-2">
                  <div>
                    <label class="text-[10px] text-gray-600">Nome Completo</label>
                    <input v-model.trim="actors.owner.name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Celular</label>
                    <input v-model.trim="actors.owner.cellphone" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">E-mail</label>
                    <input v-model.trim="actors.owner.email" type="email" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CPF</label>
                    <input v-model.trim="actors.owner.cpf" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CEP</label>
                    <input v-model.trim="actors.owner.zip_code" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Endereço</label>
                    <input v-model.trim="actors.owner.address" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Número</label>
                      <input v-model.trim="actors.owner.number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">Bairro</label>
                      <input v-model.trim="actors.owner.neighborhood" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Cidade</label>
                      <input v-model.trim="actors.owner.city" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">UF</label>
                      <input v-model.trim="actors.owner.st" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Responsável Legal (PJ) -->
              <div v-if="form.contract_person==='PJ'" class="border border-slate-200 rounded-lg bg-slate-50 p-3">
                <div class="text-xs font-semibold text-gray-700 mb-2">Responsável Legal (PJ)</div>
                <div class="grid grid-cols-1 gap-2">
                  <div>
                    <label class="text-[10px] text-gray-600">Nome Completo</label>
                    <input v-model.trim="actors.legal_responsible.name" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Celular</label>
                    <input v-model.trim="actors.legal_responsible.cellphone" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">E-mail</label>
                    <input v-model.trim="actors.legal_responsible.email" type="email" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CPF</label>
                    <input v-model.trim="actors.legal_responsible.cpf" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">CEP</label>
                    <input v-model.trim="actors.legal_responsible.zip_code" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div>
                    <label class="text-[10px] text-gray-600">Endereço</label>
                    <input v-model.trim="actors.legal_responsible.address" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Número</label>
                      <input v-model.trim="actors.legal_responsible.number" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">Bairro</label>
                      <input v-model.trim="actors.legal_responsible.neighborhood" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <label class="text-[10px] text-gray-600">Cidade</label>
                      <input v-model.trim="actors.legal_responsible.city" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                    <div>
                      <label class="text-[10px] text-gray-600">UF</label>
                      <input v-model.trim="actors.legal_responsible.st" class="w-full border rounded px-2 py-1 h-8 text-sm" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
    <template #footer>
      <div class="flex items-center justify-end gap-2">
        <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50" :disabled="!selectedDuration || saving" @click="submitEffective">Efetivar Proposta</button>
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
import Toast from '@/components/ui/Toast.vue'
import api from '@/services/axios'
import { Plus, FileDown, Printer, Search, Eraser, Eye, Edit, ChevronRight, ChevronDown, CheckCircle } from 'lucide-vue-next'

const rows = ref([])
const loading = ref(false)
const search = ref('')
const auth = useAuthStore()
const isSuperUser = computed(() => auth.user?.is_superuser === true)
// Toast state
const toast = ref({ show: false, message: '', type: 'success' })
function notify(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}
// Garante que licensed_id esteja preenchido para usuários licenciados
async function ensureLicensedId() {
  if (form.value.licensed_id) return
  const id = auth.user?.licensed_id
  if (id) {
    form.value.licensed_id = id
    return
  }
  try {
    const prof = await auth.fetchProfile()
    if (prof?.licensed_id) form.value.licensed_id = prof.licensed_id
  } catch {}
}


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
  { key: 'january', label: 'Janeiro' }, { key: 'february', label: 'Fevereiro' },
  { key: 'march', label: 'Março' }, { key: 'april', label: 'Abril' },
  { key: 'may', label: 'Maio' }, { key: 'june', label: 'Junho' },
  { key: 'july', label: 'Julho' }, { key: 'august', label: 'Agosto' },
  { key: 'september', label: 'Setembro' }, { key: 'october', label: 'Outubro' },
  { key: 'november', label: 'Novembro' }, { key: 'december', label: 'Dezembro' }
]
function isMonthMissing(key) {
  const v = Number(form.value.monthly_consumption?.[key])
  return !(v || v === 0) && v !== 0
}

function isValidZip(v) {
  const digits = String(v || '').replace(/\D/g, '')
  return digits.length === 8
}
function onPhoneInput(actorKey) {
  const only = String(actors.value[actorKey].cellphone || '').replace(/\D/g, '').slice(0, 11)
  actors.value[actorKey].cellphone = only
}
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
const showFieldErrors = ref(false)
const fieldErrors = ref({ owner: false, energy_provider_id: false, consumer_unit: false, consumer_group: false })
const showResult = ref(false)
const showResend = ref(false)
const lastResponse = ref(null)
const resend = ref({ reference: '', property_type: '', electric_bill: 0, energy_provider_id: null })
const selectedDuration = ref(null)
const showMonthly = ref(false)
const effective = ref({
  reference: '',
  contract_duration: null,
  consumer_unit: '',
  consumer_group: '',
  owner: 'Próprio',
  cellphone: '',
  installation_address: { address: '', number: '', complement: '', neighborhood: '', city: '', st: '' },
})

// Mantém endereço de instalação sincronizado com os campos do contratante
function syncContractorAddressToInstallation() {
  effective.value.installation_address.address = actors.value.contractor.address || ''
  effective.value.installation_address.number = actors.value.contractor.number || ''
  effective.value.installation_address.complement = actors.value.contractor.complement || ''
  effective.value.installation_address.neighborhood = actors.value.contractor.neighborhood || ''
  effective.value.installation_address.city = actors.value.contractor.city || ''
  effective.value.installation_address.st = actors.value.contractor.st || ''
}

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
  { key: 'contractor_name', label: 'Contractor' },
  { key: 'contractor_email', label: 'E-mail' },
  { key: 'contractor_cell', label: 'Celular' },
  { key: 'provider', label: 'Distribuidora' },
  { key: 'created', label: 'Cadastro' },
  { key: 'expired', label: 'Expira' },
  { key: 'reference', label: 'Referência' },
  { key: 'status', label: 'Status' },
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
  // Preenche automaticamente para licenciado
  if (!isSuperUser.value && auth.user?.licensed_id) {
    form.value.licensed_id = auth.user.licensed_id
  }
}

function handleCloseNew() {
  showNew.value = false
  // Reseta campos ao fechar
  editingProposal.value = null
  resetForm()
}

async function validateInitial() {
  try {
    errorMsg.value = ''
    validatedStep.value = false
    await ensureLicensedId()
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
  // limpa erros visuais ao trocar etapa
  showFieldErrors.value = false
  fieldErrors.value = { owner: false, energy_provider_id: false, consumer_unit: false, consumer_group: false }
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

    // Modo edição: apenas atualiza campos de visitas (sem alterar dados do contratante/endereços)
    if (editingProposal.value) {
      showFieldErrors.value = false
      const body = { visit_1: form.value.visit_1 || null, visit_2: form.value.visit_2 || null }
      await api.patch(`/api/contractor/proposals/${editingProposal.value.id}/`, body)
      await refreshList()
      showNew.value = false
      notify('Proposta atualizada com sucesso!','success')
      return
    }

    // Validações mínimas
    // Se estiver editando e o usuário é licenciado, não exigir manualmente o ID
    if (editingProposal.value && !form.value.licensed_id && auth.user?.licensed_id) {
      form.value.licensed_id = auth.user.licensed_id
    }
    if (!form.value.licensed_id && !editingProposal.value) throw new Error('Informe o ID do Licenciado')
    if (!form.value.zip_code) throw new Error('Informe o CEP de instalação')
    if (!form.value.contract_person) throw new Error('Informe o tipo de pessoa (PF/PJ)')
    if (form.value.contract_person === 'PJ') {
      const lr = actors.value.legal_responsible
      if (!lr.name || !lr.cpf) throw new Error('Responsável legal é obrigatório para PJ (nome e CPF)')
    }

    // Campos obrigatórios após validação inicial
    showFieldErrors.value = true
    if (!form.value.owner) throw new Error('Informe o Proprietário do Imóvel')
    if (!form.value.energy_provider_id) throw new Error('Selecione a Distribuidora')
    if (!form.value.consumer_unit) throw new Error('Informe a Unidade Consumidora')
    if (!form.value.consumer_group) throw new Error('Informe o Grupo de Consumo')
    // todos os meses devem estar presentes (zero é válido)
    for (const m of months) {
      const v = form.value.monthly_consumption?.[m.key]
      if (v === null || v === undefined || v === '') {
        throw new Error(`Informe o consumo de ${m.label}`)
      }
    }

    // Valida Nome e Sobrenome do contratante (após campos principais)
    const nameContractor = (actors.value.contractor.name || '').trim()
    if (!nameContractor || nameContractor.split(/\s+/).length < 2) {
      throw new Error('Informe nome e sobrenome do contratante')
    }
    if (!actors.value.contractor.email) {
      throw new Error('Informe o e-mail do contratante')
    }
    if (!isValidZip(actors.value.contractor.zip_code)) {
      throw new Error('Informe um CEP válido (8 dígitos) para o contratante')
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
      electric_bill: form.value.electric_bill ? Number(form.value.electric_bill) : 0,
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
    // Inicializa dados para efetivação
    initializeEffectiveData()
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
      // Sempre busca a proposta detalhada para garantir dados atuais do contractor e endereço
      let proposalData = row
      try {
        const det = await api.get(`/api/contractor/proposals/${row.id}/`)
        proposalData = det.data || row
      } catch {}
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
        // Usa SEMPRE os dados da tabela ContractorProposal (detalhe, se possível)
        proposal: proposalData,
        result: result
      }
      initializeEffectiveData()
      // Preenche owner/legal_responsible a partir de lead_actors da Proposal
      try {
        const la = Array.isArray(proposalData?.lead_actors) ? proposalData.lead_actors : []
        const owner = la.find(x => x.actor === 'owner')
        const lr = la.find(x => x.actor === 'legal_responsible')
        if (owner) {
          actors.value.owner = {
            actor: 'owner',
            name: owner.name || '',
            email: owner.email || '',
            cellphone: (owner.cellphone || ''),
            cpf: (owner.cpf_cnpj || '').toString().replace(/\D/g, ''),
            zip_code: (owner.zip_code || ''),
            address: owner.address || '',
            number: owner.number || '',
            neighborhood: owner.neighborhood || '',
            city: owner.city || '',
            st: owner.st || '',
          }
          // Se houver owner, já reflete no seletor
          if (proposalData?.owner && proposalData.owner.toLowerCase() !== 'próprio' && proposalData.owner.toLowerCase() !== 'proprio') {
            effective.value.owner = 'Outro'
          }
        }
        if (lr) {
          actors.value.legal_responsible = {
            actor: 'legal_responsible',
            name: lr.name || '',
            email: lr.email || '',
            cellphone: (lr.cellphone || ''),
            cpf: (lr.cpf_cnpj || '').toString().replace(/\D/g, ''),
            zip_code: (lr.zip_code || ''),
            address: lr.address || '',
            number: lr.number || '',
            neighborhood: lr.neighborhood || '',
            city: lr.city || '',
            st: lr.st || '',
          }
        }
      } catch {}
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
  form.value.electric_bill = Number(row.electric_bill_amount || 0)
  form.value.visit_1 = row.visit_1 ? row.visit_1.slice(0,16) : ''
  form.value.visit_2 = row.visit_2 ? row.visit_2.slice(0,16) : ''
  form.value.monthly_consumption = row.monthly_consumption || {
    january: 0, february: 0, march: 0, april: 0, may: 0, june: 0,
    july: 0, august: 0, september: 0, october: 0, november: 0, december: 0
  }
  
  // Preenche dados do contratante para visualização
  actors.value.contractor.name = row.contractor?.lead_name || row.legal_name || ''
  actors.value.contractor.email = row.contractor?.email || row.email || ''
  actors.value.contractor.cellphone = row.contractor?.cellphone || ''
  actors.value.contractor.zip_code = row.zip_code || ''
  actors.value.contractor.address = row.address || ''
  actors.value.contractor.number = row.number || ''
  actors.value.contractor.neighborhood = row.neighborhood || ''
  actors.value.contractor.city = row.city || ''
  actors.value.contractor.st = row.state || ''
  
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

function initializeEffectiveData() {
  const result = lastResponse.value?.result || {}
  const proposal = lastResponse.value?.proposal || {}
  const contrNow = proposal?.contractor || {}
  const contractPersonInit = (proposal?.contract_person || 'PF').toUpperCase()

  // Plano inicialmente pelo resultado salvo (tabela). Usuário pode trocar pelo radio
  selectedDuration.value = result.contract_duration || null
  effective.value.reference = proposal?.reference_code || ''
  effective.value.contract_duration = Number(selectedDuration.value || result.contract_duration || 0)

  // Prioriza dados atuais da Proposal/Contractor
  effective.value.consumer_unit = result.consumer_unit || proposal?.consumer_unit || ''
  effective.value.consumer_group = result.consumer_group || proposal?.consumer_group || ''
  effective.value.owner = proposal?.owner || 'Próprio'
  effective.value.cellphone = contrNow?.cellphone || ''

  effective.value.installation_address = {
    address: proposal?.address || '',
    number: proposal?.number || '',
    complement: proposal?.complement || '',
    neighborhood: proposal?.neighborhood || '',
    city: proposal?.city || '',
    st: proposal?.state || '',
  }

  actors.value.contractor = {
    actor: 'contractor',
    name: contrNow?.lead_name || proposal?.legal_name || actors.value.contractor.name || '',
    legal_name: proposal?.legal_name || actors.value.contractor.legal_name || '',
    email: contrNow?.email || proposal?.email || actors.value.contractor.email || '',
    cellphone: contrNow?.cellphone || actors.value.contractor.cellphone || '',
    cpf: contractPersonInit === 'PF' ? ((proposal?.cpf_cnpj || actors.value.contractor.cpf || '').toString().replace(/\D/g, '')) : '',
    zip_code: (proposal?.zip_code || '').toString().replace(/\D/g, ''),
    address: proposal?.address || '',
    number: proposal?.number || '',
    neighborhood: proposal?.neighborhood || '',
    city: proposal?.city || '',
    st: proposal?.state || '',
  }
}

async function submitEffective() {
  try {
    saving.value = true
    const reference = effective.value.reference || lastResponse.value?.revo?.data?.reference || lastResponse.value?.proposal?.reference_code
    const contractPerson = (form.value.contract_person || lastResponse.value?.proposal?.contract_person || 'PF').toUpperCase()

    // Monta ator contratante conforme regras PF/PJ
    const contractorActor = { ...actors.value.contractor }
    const fromProposal = lastResponse.value?.proposal || {}

    // Campos comuns
    const actorPayload = {
      actor: 'contractor',
      cellphone: String(contractorActor.cellphone || effective.value.cellphone || ''),
      email: contractorActor.email || '',
      zip_code: (contractorActor.zip_code || '').toString().replace(/\D/g, ''),
      address: contractorActor.address || effective.value.installation_address.address || '',
      number: contractorActor.number || effective.value.installation_address.number || '',
      complement: contractorActor.complement || effective.value.installation_address.complement || '',
      neighborhood: contractorActor.neighborhood || effective.value.installation_address.neighborhood || '',
      city: contractorActor.city || effective.value.installation_address.city || '',
      st: contractorActor.st || effective.value.installation_address.st || '',
    }

    if (contractPerson === 'PJ') {
      actorPayload.legal_name = contractorActor.legal_name || ''
      actorPayload.fiscal_number = (form.value.fiscal_number || '').toString().replace(/\D/g, '')
    } else {
      actorPayload.name = contractorActor.name || ''
      const cpfCandidate = (contractorActor.cpf || fromProposal.cpf_cnpj || form.value.fiscal_number || '').toString().replace(/\D/g, '')
      if (cpfCandidate && cpfCandidate.length === 11) actorPayload.cpf = cpfCandidate
    }

    // Pequenas validações para evitar erro 400 da REVO
    if (contractPerson === 'PJ') {
      if (!actorPayload.legal_name) throw new Error('Razão social do contratante é obrigatória (PJ)')
      if (!actorPayload.fiscal_number) throw new Error('CNPJ do contratante é obrigatório (PJ)')
    } else {
      if (!actorPayload.name || actorPayload.name.trim().split(/\s+/).length < 2) throw new Error('Nome completo do contratante é obrigatório (PF)')
      if (!actorPayload.cpf || actorPayload.cpf.length !== 11) throw new Error('CPF do contratante é obrigatório (PF)')
    }
    if (!actorPayload.cellphone || String(actorPayload.cellphone).length < 10) throw new Error('Celular do contratante deve ter ao menos 10 dígitos')
    if (!actorPayload.zip_code || String(actorPayload.zip_code).length !== 8) throw new Error('CEP do contratante deve ter 8 dígitos')

    // Monta owner quando não for próprio
    let ownerActor = null
    if ((effective.value.owner || '').toLowerCase() !== 'próprio' && (effective.value.owner || '').toLowerCase() !== 'proprio') {
      ownerActor = {
        actor: 'owner',
        name: actors.value.owner.name || '',
        cellphone: (actors.value.owner.cellphone || '').toString(),
        email: actors.value.owner.email || '',
        cpf: (actors.value.owner.cpf || '').toString().replace(/\D/g, ''),
        zip_code: (actors.value.owner.zip_code || '').toString().replace(/\D/g, ''),
        address: actors.value.owner.address || '',
        number: actors.value.owner.number || '',
        neighborhood: actors.value.owner.neighborhood || '',
        city: actors.value.owner.city || '',
        st: actors.value.owner.st || '',
      }
    }

    const body = {
      reference: reference,
      contract_duration: String(selectedDuration.value || effective.value.contract_duration || ''),
      cellphone: String(effective.value.cellphone || actorPayload.cellphone || ''),
      owner: effective.value.owner || 'Próprio',
      consumer_unit: effective.value.consumer_unit || null,
      consumer_group: (effective.value.consumer_group || '').toString().toUpperCase() || null,
      installation_address: { ...effective.value.installation_address },
      lead_actors: [actorPayload].concat(ownerActor ? [ownerActor] : [])
    }
    const { data } = await api.put('/api/contractor/revo/simulation/', body)
    lastResponse.value = data || lastResponse.value
    await refreshList()
    alert('Proposta efetivada com sucesso!')
  } catch (e) {
    alert(e?.response?.data?.detail || e?.message || 'Erro ao efetivar proposta')
  } finally {
    saving.value = false
  }
}
</script>


