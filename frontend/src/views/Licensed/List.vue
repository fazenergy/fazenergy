<template>
  <div class="space-y-3">
    <!-- Toolbar compacta: botões + busca -->
    <div class="mb-3 bg-white rounded">
      <div class="flex items-center gap-2 flex-wrap">
        <button v-if="isSuperadmin" @click="openNewModal" class="px-2 py-1 h-8 text-xs rounded bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm inline-flex items-center gap-1.5">
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
        <!-- Botão Info: abre modal explicando regras de Ativação -->
        <button @click="showInfo=true" class="inline-flex items-center justify-center w-9 h-9 rounded text-blue-600 hover:text-blue-700" title="Informações">
          <Info class="w-5 h-5" />
        </button>

        <div class="flex items-center gap-2 flex-1 min-w-[12rem]">
          <input v-model.trim="q" type="text" placeholder="Pesquisar..." class="flex-1 border rounded px-2 py-1 h-8 text-xs" />
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
      <DataTable :columns="columns" :rows="filtered" :loading="loading" :min-height="gridMinHeight">
        <template #title>Licenciados</template>
        <template #actions="{ row }">
          <div class="flex items-center gap-1">
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-blue-600 text-white" @click="openEdit(row)" title="Editar">
              <Pencil class="w-4 h-4" />
            </button>
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-gray-200 text-gray-700" @click="openReport(row)" title="Relatórios">
              <FileText class="w-4 h-4" />
            </button>
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-purple-600 hover:bg-purple-700 text-white" @click="openStatement(row)" title="Extrato">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4"><path d="M4 4h16v2H4V4zm0 4h10v2H4V8zm0 4h16v2H4v-2zm0 4h10v2H4v-2z"/></svg>
            </button>
            <button class="inline-flex items-center justify-center w-8 h-8 rounded bg-orange-500 hover:bg-orange-600 text-white" @click="openResetPass(row)" title="Trocar senha">
              <KeyRound class="w-4 h-4" />
            </button>
          </div>
        </template>
        <template #col:upline="{ row }">
          <button class="px-2 py-1 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white" @click="openUpline(row)">Ver Upline</button>
        </template>
        <template #col:avatar="{ row }" text-align="center">
          <img :src="avatarUrl(row)" class="w-8 h-8 rounded-full object-cover" loading="lazy" />
        </template>
        <template #col:nameLogin="{ row }">
          <div class="text-[12px] leading-tight">
            <div>{{ (row.user?.full_name || fullName(row) || '-') }}</div>
            <div><b>Login:</b> {{ row.user?.username || '-' }}</div>
          </div>
        </template>
        <template #col:career="{ row }">{{ row.current_career?.stage_name || 'nenhuma' }}</template>
        <template #col:created="{ row }">{{ formatDate(row.dtt_record) }}</template>
        <template #col:city="{ row }">{{ (row.city_lookup?.name || '-') + (row.city_lookup?.state ? ('-' + (row.city_lookup.state.uf||'')) : '') }}</template>
        <template #col:plan="{ row }">{{ row.plan?.name || '-' }}</template>
        <template #col:payment="{ row }">
          <!-- Badge de pagamento: usa payment_status vindo do backend (confirmed, pending, canceled) -->
          <span :class="paymentBadgeClass(row.payment_status)">{{ paymentLabel(row.payment_status) }}</span>
        </template>
        <template #col:status="{ row }">
          <!-- Status exibido pela REGRA DE NEGÓCIO (derivado): pagamento confirmado + documentos aprovados.
               Mantemos o flag administrativo (stt_record) apenas no tooltip para auditoria. -->
          <div class="w-full flex justify-center">
            <span :class="statusBadgeClass(row.is_active)" :title="statusTooltip(row)">{{ row.is_active ? 'Ativo' : 'Inativo' }}</span>
          </div>
        </template>
        <!-- Nova coluna: Documentos -->
        <!-- Regras de exibição:
             - pending  => Pendente (badge âmbar)
             - approved => Validados (badge verde)
             - rejected => Reprovado (badge vermelha)
           Observação: valor vem de Licensed.stt_document (exposto na listagem). -->
        <template #col:docs="{ row }">
          <span :class="docsBadgeClass(mapDocStatus(row))">{{ docLabel(mapDocStatus(row)) }}</span>
        </template>
      </DataTable>
    </div>

    <!-- Modal Upline -->
    <Modal v-model="showUpline" :header-blue="true" :no-header-border="true">
      <template #title>Upline</template>
      <div class="w-[720px] max-w-[90vw]">
        <div v-if="uplineLoading" class="py-8 text-center text-sm text-gray-500">Carregando...</div>
        <table v-else class="w-full text-sm">
          <thead>
            <tr class="bg-blue-800 text-white">
              <th class="px-3 py-2 text-left">Upline</th>
              <th class="px-3 py-2 text-right">Nível</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in uplineChain" :key="u.id" class="even:bg-gray-50">
              <td class="px-3 py-2">{{ u.full_name || u.username }} <span class="text-gray-500">| {{ u.username }}</span></td>
              <td class="px-3 py-2 text-right">{{ u.level }}</td>
            </tr>
            <tr v-if="!uplineChain.length">
              <td colspan="2" class="px-3 py-4 text-center text-gray-500">Sem upline.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Modal>

    <!-- Modal Extrato -->
    <Modal v-model="showStatement" :header-blue="true" :no-header-border="true">
      <template #title>Extrato Virtual</template>
      <div class="w-[920px] max-w-[95vw] h-[70vh] max-h-[70vh] flex flex-col">
        <div class="shrink-0 flex items-center justify-between mb-3">
          <div class="text-sm text-gray-700">Distribuidor: <b>{{ statementTarget?.user?.username }}</b></div>
          <div class="text-sm text-gray-700">Saldo Disponível: <b>R$ {{ Number(statementBalance).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</b> — Bloqueado: <b>R$ {{ Number(statementBlocked).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</b></div>
          <div class="flex items-center gap-2">
            <select v-model.number="statementMonth" class="border rounded px-2 py-1 text-sm" @change="loadStatement">
              <option v-for="m in 12" :key="m" :value="m">{{ String(m).padStart(2,'0') }}</option>
            </select>
            <select v-model.number="statementYear" class="border rounded px-2 py-1 text-sm" @change="loadStatement">
              <option v-for="y in [statementYear-1, statementYear, statementYear+1]" :key="y" :value="y">{{ y }}</option>
            </select>
            <button @click="exportStatementXls" class="px-2 py-1 h-8 text-xs rounded bg-purple-600 hover:bg-purple-700 text-white inline-flex items-center gap-1.5">
              <FileDown class="w-4 h-4" />
              <span>XLS</span>
            </button>
            <button @click="printStatement" class="px-2 py-1 h-8 text-xs rounded bg-blue-600 hover:bg-blue-700 text-white inline-flex items-center gap-1.5">
              <Printer class="w-4 h-4" />
              <span>Imprimir</span>
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-auto">
          <div v-if="statementLoading" class="py-8 text-center text-sm text-gray-500">Carregando...</div>
          <table v-else class="w-full text-sm">
            <thead>
              <tr class="bg-blue-800 text-white">
                <th class="px-3 py-2 text-left">ID</th>
                <th class="px-3 py-2 text-left">Data Cadastro</th>
                <th class="px-3 py-2 text-left">Referência</th>
                <th class="px-3 py-2 text-left">Descrição</th>
                <th class="px-3 py-2 text-right">Valor</th>
                <th class="px-3 py-2 text-left">Operação</th>
                <th class="px-3 py-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in pagedStatementRows" :key="t.id" class="even:bg-gray-50">
                <td class="px-3 py-2">{{ t.id }}</td>
                <td class="px-3 py-2">{{ new Date(t.dtt_record).toLocaleString('pt-BR') }}</td>
                <td class="px-3 py-2">{{ statementReferenceLabel(t) }}</td>
                <td class="px-3 py-2">{{ t.description || t.product }}</td>
                <td class="px-3 py-2 text-right">{{ Number(t.amount).toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</td>
                <td class="px-3 py-2">{{ t.operation === 'credit' ? 'Crédito' : 'Débito' }}</td>
                <td class="px-3 py-2">{{ t.status }}</td>
              </tr>
              <tr v-if="!statementRows.length">
                <td colspan="7" class="px-3 py-4 text-center text-gray-500">Sem transações no período.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="statementRows.length" class="shrink-0 mt-2 pt-2 border-t flex items-center justify-between text-sm bg-white">
          <div>
            <span class="font-medium">Total:</span>
            R$ {{ totalStatement.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}
            <span class="ml-2 text-gray-500">({{ statementRows.length }} lançamentos)</span>
          </div>
          <div class="flex items-center gap-2">
            <button class="px-2 py-1 rounded border" :disabled="statementPage===1" @click="statementPage = Math.max(1, statementPage-1)">Anterior</button>
            <span>Página {{ statementPage }} / {{ statementTotalPages }}</span>
            <button class="px-2 py-1 rounded border" :disabled="statementPage===statementTotalPages" @click="statementPage = Math.min(statementTotalPages, statementPage+1)">Próxima</button>
            <select v-model.number="statementPageSize" class="ml-2 border rounded px-2 py-1">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
          </div>
        </div>
      </div>
    </Modal>
    <!-- Modal Info (regras de ativação) -->
    <Modal v-model="showInfo" :header-blue="true" :no-header-border="true">
      <template #title>Regras de Ativação</template>
      <!-- Layout em uma coluna com ícones, largura mais compacta e bom respiro -->
      <div class="w-[480px] max-w-[90vw] px-5 py-4">
        <div class="space-y-4">
          <p class="text-[13px] leading-6">
            O cadastro é considerado <b>Ativo</b> quando há <b>pagamento da adesão confirmado</b>
            e <b>documentação aprovada</b>.
          </p>
          <div class="grid grid-cols-1 gap-3">
            <div class="flex items-start gap-2">
              <CreditCard class="w-4 h-4 text-blue-600 mt-1" />
              <p class="text-[13px] leading-6">Se o pagamento for confirmado antes da aprovação dos documentos, o usuário permanece pendente até a aprovação.</p>
            </div>
            <div class="flex items-start gap-2">
              <FileCheck class="w-4 h-4 text-blue-600 mt-1" />
              <p class="text-[13px] leading-6">Se os documentos forem aprovados antes do pagamento, o usuário permanece pendente até a confirmação do pagamento.</p>
            </div>
            <div class="flex items-start gap-2">
              <Clock class="w-4 h-4 text-blue-600 mt-1" />
              <p class="text-[13px] leading-6">A avaliação ocorre automaticamente em ambos os eventos.</p>
            </div>
            <div class="flex items-start gap-2">
              <CheckCircle class="w-4 h-4 text-emerald-600 mt-1" />
              <p class="text-[13px] leading-6">Quando ambos os critérios são atendidos, o sistema marca o cadastro como <b>Ativo</b> e registra a <b>data de ativação</b>.</p>
            </div>
          </div>
          <hr class="border-gray-200" />
          <div class="space-y-2">
            <div class="font-semibold text-sm">Status da coluna "Documentos"</div>
            <ul class="text-[13px] leading-6 list-disc ml-5 space-y-1">
              <li><b>Pendente</b>: licenciado ainda não enviou os documentos.</li>
              <li><b>Aguardando Aprovação</b>: documentos enviados, aguardando análise do operador.</li>
              <li><b>Aprovado</b>: documentos validados e aprovados.</li>
            </ul>
          </div>
        </div>
      </div>
    </Modal>
    <!-- Modal Trocar Senha -->
    <Modal v-model="showResetPass" :header-blue="true" :no-header-border="true">
      <template #title>Trocar Senha</template>
      <div v-if="resetTarget" class="relative" :key="rpKey">
        <div v-if="rpMsg" class="mb-3 px-3 py-2 rounded bg-blue-50 text-blue-700 border border-blue-200 text-sm relative">
          {{ rpMsg }}
          <button class="absolute right-2 top-1/2 -translate-y-1/2 text-blue-700 hover:text-blue-900" @click="rpMsg=''" aria-label="Fechar">×</button>
        </div>
        <!-- Campos fantasmas para evitar autofill do navegador -->
        <div style="position:absolute; left:-10000px; top:auto; width:1px; height:1px; overflow:hidden;" aria-hidden="true">
          <input type="text" name="username" autocomplete="username" tabindex="-1" />
          <input type="password" name="password" autocomplete="current-password" tabindex="-1" />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-6 gap-4 text-sm">
          <FormField label="Nome" class="md:col-span-3">
            <Input :model-value="fullName(resetTarget)" readonly />
          </FormField>
          <FormField label="Usuário" class="md:col-span-3">
            <Input :model-value="resetTarget.user?.username || ''" readonly />
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

    <!-- Modal Relatório -->
    <Modal v-model="showReport" :header-blue="true" :no-header-border="true">
      <template #title>Relatório do Licenciado</template>
      <div v-if="current">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div><b>Nome Completo:</b> {{ fullName(current) }}</div>
          <div><b>Login:</b> {{ current.user?.username }}</div>
          <div><b>Indicador Original:</b>
            <template v-if="current.original_indicator?.user?.username">
              <button class="text-blue-600 hover:underline" @click="openReportByUsername(current.original_indicator.user.username)">{{ current.original_indicator.user.username }}</button>
            </template>
            <template v-else>-</template>
          </div>
          <div><b>Plano atual:</b> {{ current.plan?.name || '-' }}</div>
          <div><b>Está ativo?</b> {{ current.stt_record ? 'Sim' : 'Não' }}</div>
          <div><b>Data de ativação:</b> {{ formatDate(current.dtt_activation) }}</div>
          <div><b>Diretos efetivados:</b> {{ current.stats?.directs_confirmed || 0 }}</div>
          <div><b>Diretos pré-cadastrados:</b> {{ current.stats?.directs_preregistered || 0 }}</div>
          <div><b>Compras realizadas:</b> {{ current.stats?.self_purchases || 0 }}</div>
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

    <!-- Modal Edição (campos restritos) -->
    <Modal v-model="showEdit" :header-blue="true" :no-header-border="true">
      <template #title>Editar Licenciado</template>
      <div v-if="form" class="relative">
        <LoadingOverlay v-if="saving" />
        <div v-if="editMsg" class="mb-3 px-3 py-2 rounded bg-blue-50 text-blue-700 border border-blue-200 text-sm relative">
          {{ editMsg }}
          <button class="absolute right-2 top-1/2 -translate-y-1/2 text-blue-700 hover:text-blue-900" @click="editMsg=''" aria-label="Fechar">×</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-6 gap-4 text-sm">
          <!-- Avatar à esquerda -->
          <div class="md:col-span-1">
            <label class="text-xs text-gray-600">Foto</label>
            <div class="mt-1 w-28 h-28 rounded-md bg-gray-100 border overflow-hidden flex items-center justify-center">
              <img :src="previewPhoto || avatarUrl(current)" v-if="(previewPhoto || avatarUrl(current))" class="w-full h-full object-cover" />
            </div>
            <div class="mt-2">
              <button type="button" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm" @click="triggerPhoto">Trocar foto</button>
              <input ref="photo" type="file" class="hidden" @change="onPhotoChange" />
            </div>
          </div>

          <!-- Form em layout igual ao pré-cadastro -->
          <div class="md:col-span-5 grid grid-cols-1 md:grid-cols-6 gap-4">
            <!-- Linha 1 -->
            <FormField label="Nome" class="md:col-span-3">
              <Input v-model="form.first_name" class="text-sm" />
            </FormField>
            <FormField label="Sobrenome" class="md:col-span-3">
              <Input v-model="form.last_name" class="text-sm" />
            </FormField>

            <!-- Linha 2 -->
            <FormField label="Email" class="md:col-span-3">
              <Input v-model="form.email" type="email" class="text-sm" />
            </FormField>
            <FormField label="Usuário" class="md:col-span-3">
              <Input v-model="form.username" class="text-sm bg-gray-100" :disabled="true" />
            </FormField>

            <!-- Linha 3 -->
            <FormField label="Telefone" class="md:col-span-3">
              <Input v-model="form.phone" class="text-sm" mask="(##) #####-####" />
            </FormField>

            <!-- Linha 4 -->
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

            <!-- Linha 5 -->
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
          <button class="px-4 py-2 rounded border text-sm" :disabled="saving" @click="showEdit=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm inline-flex items-center gap-2 disabled:opacity-60" :disabled="saving" @click="saveEdit">
            <span v-if="saving" class="inline-block h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
            <span>{{ saving ? 'Gravando...' : 'Gravar' }}</span>
          </button>
        </div>
      </template>
    </Modal>
    <!-- Modal Cadastro (aproveita o formulário existente do pré-cadastro) -->
    <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
      <template #title>Novo Licenciado</template>
      <FormPreRegister :in-modal="true" @close="showNew=false" />
      <template #footer>
        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 rounded border" @click="showNew=false">Fechar</button>
          <button class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white" @click="submitPreForm">Gravar</button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import api from '@/services/axios'
import { API_BASE_URL } from '@/config/settings'
import Modal from '@/components/ui/Modal.vue'
import DataTable from '@/components/ui/DataTable.vue'
import { FileText, Pencil, KeyRound, Plus, FileDown, Printer, Search, Eraser, Info, CreditCard, FileCheck, Clock, CheckCircle } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import InputPass from '@/components/ui/InputPass.vue'
import FormField from '@/components/ui/FormField.vue'
import FormPreRegister from '@/components/FormPreRegister.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const list = ref([])
const q = ref('')
const filtered = computed(() => {
  const term = (q.value || '').toLowerCase()
  return list.value.filter(lic => !term || (lic.user?.username||'').toLowerCase().includes(term) || ((lic.user?.first_name||'') + ' ' + (lic.user?.last_name||'')).toLowerCase().includes(term))
})

const showReport = ref(false)
const current = ref(null)
const showEdit = ref(false)
const initializingEdit = ref(false)
const form = ref(null)
const saving = ref(false)
const photo = ref(null)
const showNew = ref(false)
const showInfo = ref(false)
const showResetPass = ref(false)
const resetTarget = ref(null)
const rpForm = ref({ password: '', confirm: '', forceChange: false })
const rpSaving = ref(false)
const rpMsg = ref('')
const rpKey = ref(0)
const isSuperadmin = computed(() => auth.user?.is_superuser || auth.user?.groups?.includes('Superadmin'))
const states = ref([])
const cities = ref([])
const previewPhoto = ref('')
const showUpline = ref(false)
const uplineChain = ref([])
const uplineLoading = ref(false)
const showStatement = ref(false)
const statementLoading = ref(false)
const statementRows = ref([])
const statementPage = ref(1)
const statementPageSize = ref(10)
const statementMonth = ref(new Date().getMonth() + 1)
const statementYear = ref(new Date().getFullYear())
const statementTarget = ref(null)
const statementBalance = ref(0)
const statementBlocked = ref(0)
const reportUpline = ref([])
const pwError = ref('')
const pwConfirmError = ref('')
const editMsg = ref('')

function submitPreForm() {
  try {
    const formEl = document.getElementById('preRegisterForm')
    if (formEl && typeof formEl.requestSubmit === 'function') {
      formEl.requestSubmit()
    } else if (formEl) {
      formEl.submit()
    }
  } catch {}
}

function openNewModal() {
  showNew.value = true
}

function formatDate(dt) { try { return new Date(dt).toLocaleString('pt-BR') } catch { return '-' } }
function fullName(lic) { return (lic.user?.first_name||'') + ' ' + (lic.user?.last_name||'') }
function docLabel(st) { return ({ pending: 'Pendente', incomplete: 'Incompleto', awaiting: 'Aguardando aprovação', approved: 'Aprovado', rejected: 'Reprovado' })[st] || '-' }

function docsBadgeClass(st) {
  // Versão em bloco ocupando a largura inteira da célula
  switch (st) {
    case 'approved':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200'
    case 'incomplete':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-rose-50 text-rose-700 border border-rose-200'
    case 'awaiting':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-blue-50 text-blue-700 border border-blue-200'
    case 'rejected':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-rose-50 text-rose-700 border border-rose-200'
    case 'pending':
    default:
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-amber-50 text-amber-700 border border-amber-200'
  }
}

// Mapeia prioridade de status para exibição
function mapDocStatus(row) {
  // Preferir status derivado quando fornecido
  if (row.documents_status) return row.documents_status
  return row.stt_document || 'pending'
}

// Pagamento: labels e badges
function paymentLabel(v) {
  const map = { confirmed: 'Confirmado', pending: 'Pendente', canceled: 'Cancelado' }
  return map[v] || '-'
}

function paymentBadgeClass(v) {
  switch (v) {
    case 'confirmed':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200'
    case 'canceled':
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-rose-50 text-rose-700 border border-rose-200'
    case 'pending':
    default:
      return 'block w-full text-center px-2 py-1 rounded text-[12px] font-medium bg-amber-50 text-amber-700 border border-amber-200'
  }
}

// Tooltip: explica por que está ativo/inativo, com base nos campos enviados pelo backend
// Regra exibida = is_active (derivado no backend): (has_paid_adesion && stt_document === 'approved')
// Mostramos também o flag administrativo atual (stt_record) para auditoria
function statusTooltip(row) {
  const paid = row.has_paid_adesion ? 'Pagamento: ok' : 'Pagamento: pendente'
  const docs = row.stt_document === 'approved' ? 'Documentos: aprovados' : (row.stt_document === 'rejected' ? 'Documentos: reprovados' : 'Documentos: pendentes')
  const derived = !!row.is_active
  const admin = row.stt_record ? 'Flag atual: Ativo' : 'Flag atual: Inativo'
  return `${paid} | ${docs} | Ativo (recomendado): ${derived ? 'Sim' : 'Não'} | ${admin}`
}

async function fetchList() {
  const { data } = await api.get('/api/core/licensed/')
}

onMounted(async () => {
  // Lista de licenciados simples usando endpoint licensed do core
  try {
    await reloadList()
  } catch (e) {
    list.value = []
  }
  try {
    const { data: s } = await api.get('/api/location/states/')
    states.value = s || []
  } catch {}
  updateGridHeight()
  window.addEventListener('resize', updateGridHeight)
})
onUnmounted(() => window.removeEventListener('resize', updateGridHeight))

async function openReport(lic) {
  current.value = lic
  showReport.value = true
  try {
    const { data } = await api.get('/api/network/upline-chain/', { params: { licensed_id: lic.id } })
    reportUpline.value = data?.chain || []
  } catch {
    reportUpline.value = []
  }
}

function openReportByUsername(uname) {
  if (!uname) return
  const lic = list.value.find(r => (r.user?.username || '').toLowerCase() === String(uname).toLowerCase())
  if (lic) {
    openReport(lic)
  }
}
function openResetPass(lic) {
  resetTarget.value = lic
  rpForm.value = { password: '', confirm: '', forceChange: false }
  rpMsg.value = ''
  rpKey.value++
  showResetPass.value = true
}
async function saveResetPass() {
  if (!isSenhaSegura(rpForm.value.password)) {
    rpMsg.value = 'Senha inválida. Use ao menos 6 caracteres, com letra, número e símbolo.'
    return
  }
  if (rpForm.value.password !== rpForm.value.confirm) {
    rpMsg.value = 'As senhas não coincidem.'
    return
  }
  rpSaving.value = true
  try {
    const licensedId = resetTarget.value?.id
    if (!licensedId) throw new Error('Licenciado inválido')
    // Atualiza a senha via mesma action de user (somente password)
    const fd = new FormData()
    fd.append('password', rpForm.value.password)
    await api.patch(`/api/core/licensed/${licensedId}/user/`, fd)
    // TODO opcional: se houver backend para forceChange, enviar flag
    showResetPass.value = false
  } catch (e) {
    rpMsg.value = 'Não foi possível trocar a senha.'
  } finally {
    rpSaving.value = false
  }
}
async function openEdit(lic) {
  current.value = lic
  form.value = {
    first_name: lic.user?.first_name || '',
    last_name: lic.user?.last_name || '',
    username: lic.user?.username || '',
    email: lic.user?.email || '',
    password: '',
    phone: lic.phone || '',
    cpf_cnpj: lic.cpf_cnpj || '',
    cep: lic.cep || '',
    address: lic.address || '',
    number: lic.number || '',
    complement: lic.complement || '',
    district: lic.district || '',
    state_id: lic.city_lookup?.state?.id || null,
    city_id: lic.city_lookup?.id || null
  }
  previewPhoto.value = ''
  // Evita que o watcher limpe a cidade durante a inicialização
  initializingEdit.value = true
  try {
    if (form.value.state_id) {
      await loadCities(form.value.state_id)
      // Reaplica a cidade após carregar a lista
      form.value.city_id = lic.city_lookup?.id || null
    } else {
      cities.value = []
    }
  } finally {
    initializingEdit.value = false
  }
  showEdit.value = true
}

function applySearch() {}

async function saveEdit() {
  saving.value = true
  try {
    const editingSelf = auth.user?.username === (current.value?.user?.username || '')
    // Valida senha do modal de edição (se informada)
    // Campos de senha foram removidos do modal de edição; validação desativada
    if (editingSelf) {
      // Atualiza perfil do usuário atual (user + licensed)
  const fd = new FormData()
      if (form.value.username && form.value.username !== (current.value?.user?.username || '')) {
        fd.append('username', form.value.username)
      }
      fd.append('first_name', form.value.first_name || '')
      fd.append('last_name', form.value.last_name || '')
      fd.append('email', form.value.email || '')
      if (form.value.phone) fd.append('phone', form.value.phone)
  if (form.value.password) fd.append('password', form.value.password)
      if (form.value.cpf_cnpj) fd.append('cpf_cnpj', form.value.cpf_cnpj)
      if (form.value.cep) fd.append('cep', form.value.cep)
      if (form.value.address) fd.append('address', form.value.address)
      if (form.value.number) fd.append('number', form.value.number)
      if (form.value.complement) fd.append('complement', form.value.complement)
      if (form.value.district) fd.append('district', form.value.district)
  if (form.value.city_id) fd.append('city_lookup', form.value.city_id)
  if (photo.value?.files?.[0]) fd.append('image_profile', photo.value.files[0])
  await api.patch('/api/core/profile/', fd)
    } else {
      // Operador/Superadmin editando outro licenciado
      const licensedId = current.value?.id
      if (!licensedId) throw new Error('LicensedId inválido para atualização')

      // 1) Atualiza dados do User do licenciado via action permitida
      const fdUser = new FormData()
      if (form.value.username && form.value.username !== (current.value?.user?.username || '')) {
        fdUser.append('username', form.value.username)
      }
      fdUser.append('first_name', form.value.first_name || '')
      fdUser.append('last_name', form.value.last_name || '')
      fdUser.append('email', form.value.email || '')
      if (form.value.password) fdUser.append('password', form.value.password)
      if (photo.value?.files?.[0]) fdUser.append('image_profile', photo.value.files[0])
      await api.patch(`/api/core/licensed/${licensedId}/user/`, fdUser)

      // 2) Atualiza dados do Licensed (endereço/contato)
      const payload = {}
      if (form.value.phone) payload['phone'] = form.value.phone
      if (form.value.cpf_cnpj) payload['cpf_cnpj'] = form.value.cpf_cnpj
      if (form.value.cep) payload['cep'] = form.value.cep
      if (form.value.address) payload['address'] = form.value.address
      if (form.value.number) payload['number'] = form.value.number
      if (form.value.complement) payload['complement'] = form.value.complement
      if (form.value.district) payload['district'] = form.value.district
      if (form.value.city_id) payload['city_lookup'] = form.value.city_id
      if (Object.keys(payload).length) {
        await api.patch(`/api/core/licensed/${licensedId}/`, payload)
      }
    }
  showEdit.value = false
    // Recarrega a lista para refletir alterações (nome, cidade, avatar etc.)
    await reloadList()
  } catch (e) {
    const status = e?.response?.status
    const data = e?.response?.data
    console.error('Erro ao gravar perfil', status, data)
    if (status === 401) {
      editMsg.value = 'Sua sessão expirou. Faça login novamente e tente salvar.'
      return
    }
    let msg = 'Não foi possível gravar. Verifique os campos obrigatórios e tente novamente.'
    if (data && typeof data === 'object') {
      try {
        const firstKey = Object.keys(data)[0]
        const firstVal = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey]
        if (firstKey && firstVal) msg = `${firstKey}: ${firstVal}`
      } catch {}
    }
    editMsg.value = msg
  } finally {
    saving.value = false
  }
}

async function resetPass(lic) {
  alert('Reset de senha enviado para: ' + (lic.user?.username || '-'))
}

function onPhotoChange(e) {
  const f = e?.target?.files?.[0]
  if (!f) { previewPhoto.value = ''; return }
  const r = new FileReader()
  r.onload = () => { previewPhoto.value = r.result }
  r.readAsDataURL(f)
}

function triggerPhoto() {
  try { photo.value?.click() } catch {}
}

async function loadCities(stateId) {
  try {
    const { data } = await api.get('/api/location/cities/', { params: { state: stateId } })
    cities.value = data || []
  } catch { cities.value = [] }
}

// Preenchimento automático via CEP (viacep)
async function onCepInput() {
  try {
    const digits = String(form.value.cep || '').replace(/\D/g, '')
    if (digits.length !== 8) return
    const res = await fetch(`https://viacep.com.br/ws/${digits}/json/`).then(r => r.json())
    if (!res || res.erro) return
    // Endereço/bairro
    form.value.address = res.logradouro || form.value.address
    form.value.district = res.bairro || form.value.district

    // Estado -> encontra pelo UF e carrega cidades
    const uf = String(res.uf || '').toUpperCase()
    const state = (states.value || []).find(s => String(s.uf).toUpperCase() === uf)
    if (state) {
      form.value.state_id = state.id
      await loadCities(state.id)
      // Cidade por nome (normalizada)
      const normalize = s => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()
      const city = (cities.value || []).find(c => normalize(c.name) === normalize(res.localidade))
      if (city) form.value.city_id = city.id
    }
  } catch {}
}

async function reloadList() {
  try {
    const { data } = await api.get('/api/core/licensed/')
    list.value = data?.results || data || []
  } catch {
    list.value = []
  }
}

async function openUpline(row) {
  try {
    showUpline.value = true
    uplineLoading.value = true
    uplineChain.value = []
    const id = row?.id
    const { data } = await api.get('/api/network/upline-chain/', { params: { licensed_id: id } })
    uplineChain.value = data?.chain || []
  } catch {
    uplineChain.value = []
  } finally {
    uplineLoading.value = false
  }
}

async function openStatement(row) {
  showStatement.value = true
  statementTarget.value = row
  await loadStatement()
}

async function loadStatement() {
  try {
    statementLoading.value = true
    statementRows.value = []
    const uname = statementTarget.value?.user?.username
    const { data } = await api.get('/api/finance/transactions/', { params: { licensed_username: uname, month: statementMonth.value, year: statementYear.value } })
    statementRows.value = data || []
    // saldo
    try {
      const { data: bal } = await api.get('/api/finance/virtual-account/balance/', { params: { licensed_username: uname } })
      statementBalance.value = bal?.balance_available || 0
      statementBlocked.value = bal?.balance_blocked || 0
    } catch {}
  } catch {
    statementRows.value = []
  } finally {
    statementLoading.value = false
  }
}

const pagedStatementRows = computed(() => {
  const start = (statementPage.value - 1) * statementPageSize.value
  return (statementRows.value || []).slice(start, start + statementPageSize.value)
})
const statementTotalPages = computed(() => {
  const len = (statementRows.value || []).length
  return Math.max(1, Math.ceil(len / statementPageSize.value))
})
watch([statementRows, statementPageSize], () => {
  statementPage.value = 1
})
const totalStatement = computed(() => {
  return (statementRows.value || []).reduce((acc, t) => acc + Number(t.amount || 0) * (t.operation === 'debit' ? -1 : 1), 0)
})

function exportStatementXls() {
  const header = ['ID', 'Data Cadastro', 'Referência', 'Descrição', 'Valor', 'Operação', 'Status']
  const rowsHtml = (statementRows.value || []).map(t => (
    `<tr>`+
    `<td>${t.id ?? ''}</td>`+
    `<td>${t.dtt_record ? new Date(t.dtt_record).toLocaleString('pt-BR') : ''}</td>`+
    `<td>${statementReferenceLabel(t)}</td>`+
    `<td>${t.description || t.product || ''}</td>`+
    `<td>${Number(t.amount||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>`+
    `<td>${t.operation === 'credit' ? 'Crédito' : 'Débito'}</td>`+
    `<td>${t.status || ''}</td>`+
    `</tr>`
  )).join('')

  const html = `\uFEFF<html><head><meta charset="utf-8" /></head><body><table border="1">`+
               `<thead><tr>${header.map(h=>`<th>${h}</th>`).join('')}</tr></thead>`+
               `<tbody>${rowsHtml}</tbody></table></body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const ym = `${String(statementYear.value)}_${String(statementMonth.value).padStart(2,'0')}`
  a.download = `extrato_${statementTarget.value?.user?.username || 'licenciado'}_${ym}.xls`
  a.click()
  URL.revokeObjectURL(url)
}

function printStatement() {
  const win = window.open('', '_blank')
  const rowsHtml = (statementRows.value || []).map(t => (
    `<tr>`+
    `<td>${t.id ?? ''}</td>`+
    `<td>${t.dtt_record ? new Date(t.dtt_record).toLocaleString('pt-BR') : ''}</td>`+
    `<td>${statementReferenceLabel(t)}</td>`+
    `<td>${t.description || t.product || ''}</td>`+
    `<td style="text-align:right">${Number(t.amount||0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>`+
    `<td>${t.operation === 'credit' ? 'Crédito' : 'Débito'}</td>`+
    `<td>${t.status || ''}</td>`+
    `</tr>`
  )).join('')
  const ym = `${String(statementYear.value)}-${String(statementMonth.value).padStart(2,'0')}`
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
    <title>Extrato Virtual</title>
    <style>
      body{font-family: Arial, sans-serif;}
      table{width:100%;border-collapse:collapse}
      th,td{border:1px solid #ddd;padding:6px;font-size:12px}
      th{background:#1e40af;color:#fff}
      .meta{margin:10px 0;font-size:12px}
    </style>
  </head><body onload="window.print()">
    <h3>Extrato Virtual</h3>
    <div class="meta">Usuário: <b>${statementTarget.value?.user?.username || ''}</b> | Período: <b>${ym}</b> | Saldo Disponível: <b>R$ ${Number(statementBalance.value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</b> — Bloqueado: <b>R$ ${Number(statementBlocked.value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</b></div>
    <table>
      <thead><tr><th>ID</th><th>Data Cadastro</th><th>Referência</th><th>Descrição</th><th>Valor</th><th>Operação</th><th>Status</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>
  </body></html>`
  win.document.write(html)
  win.document.close()
}

function statementReferenceLabel(t) {
  // Preferência por origem deduzida (quando backend informar)
  if (t.origin_model) {
    const model = String(t.origin_model).toLowerCase()
    if (model.includes('plan') || model.includes('adesion') || model.includes('adesao')) return 'Adesão'
    if (model.includes('proposal') || model.includes('contractor') || model.includes('plant')) return 'Usina'
  }
  // Fallback por texto do produto/descrição
  const txt = `${t.product || ''} ${t.description || ''}`.toLowerCase()
  if (/(ades[aã]o|plan)/.test(txt)) return 'Adesão'
  if (/(usina|proposta|contrato|energia)/.test(txt)) return 'Usina'
  return '—'
}

// Regras de senha (mesmas do pré-cadastro)
function isSenhaSegura(senha) {
  if (!senha || typeof senha !== 'string') return false
  return (
    senha.length >= 6 && /[a-zA-Z]/.test(senha) && /\d/.test(senha) && /[^a-zA-Z0-9]/.test(senha)
  )
}

watch(() => form.value?.password, (senha) => {
  if (!senha) { pwError.value = ''; return }
  pwError.value = isSenhaSegura(senha) ? '' : 'Senha fraca'
})

watch(() => form.value?.password_confirm, (conf) => {
  if (!form.value) return
  pwConfirmError.value = conf === form.value.password ? '' : 'As senhas não coincidem'
})

watch(() => form.value?.state_id, async (nv, ov) => {
  if (nv) {
    await loadCities(nv)
    // Limpa cidade somente quando usuário alterar estado, não na carga inicial
    if (!initializingEdit.value && ov !== undefined) {
      form.value.city_id = null
    }
  } else {
    cities.value = []
    form.value.city_id = null
  }
})

// DataTable columns e altura dinâmica
const columns = [
  { key: 'avatar', label: 'Avatar', width: 'w-[64px]' },
  { key: 'nameLogin', label: 'Nome/Login', width: 'w-auto' },
  { key: 'career', label: 'Qualificação' },
  { key: 'created', label: 'Dtt Cadastro' },
  { key: 'city', label: 'Cidade-UF' },
  { key: 'plan', label: 'Plano' },
  // Coluna Pagamento da Adesão (badge por status)
  { key: 'payment', label: 'Pagamento' },
  // Coluna Documentos (status de validação, vindo de Licensed.stt_document)
  { key: 'docs', label: 'Documentos' },
  // Status deve ser a última coluna do grid
  { key: 'status', label: 'Status' },
]

const gridWrapper = ref(null)
const gridMinHeight = ref('300px')
function updateGridHeight() {
  if (!gridWrapper.value) return
  const rect = gridWrapper.value.getBoundingClientRect()
  const available = window.innerHeight - rect.top - 16
  gridMinHeight.value = `${Math.max(available, 300)}px`
}

function fullNameOrUsername(row) {
  const fn = row.user?.first_name || ''
  const ln = row.user?.last_name || ''
  const full = `${fn} ${ln}`.trim()
  return full || (row.user?.username || '-')
}

function statusBadgeClass(active) {
  return active
    ? 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-800 border border-emerald-300'
    : 'inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-700 border border-gray-300'
}

function avatarUrl(obj) {
  const user = obj?.user || obj
  const url =
    user?.image_profile ||
    user?.image ||
    user?.avatar ||
    obj?.avatar ||
    obj?.image ||
    obj?.image_profile ||
    ''
  if (!url) return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="100%" height="100%" fill="%23e5e7eb"/></svg>'
  // Se a API devolve caminho relativo, prefixa com API_BASE_URL (backend)
  if (/^https?:\/\//i.test(url)) return url
  const pref = url.startsWith('/') ? url : `/${url}`
  return `${API_BASE_URL}${pref}`
}
</script>


