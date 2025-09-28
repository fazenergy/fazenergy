<!-- src/views/Dashboard.vue -->
<!-- src/views/Dashboard.vue -->
<template>
<div class="space-y-3">
<div class="mb-3 bg-white rounded">
<div class="flex items-center justify-between gap-2 px-2 py-2">
  <div class="flex items-center gap-2 flex-wrap">
   <!-- ✅ Botão visível para SUPERADMIN -->
    <button
      v-if="isSuperadmin || isLicensed"
      @click="showNew = true"
      class="h-8 px-3 text-xs bg-blue-600 text-white hover:bg-blue-700 inline-flex items-center gap-1"
    >
      <Plus class="w-4 h-4" />
      Cadastrar Licenciado
    </button>
    <button
      v-if="isLicensed || isSuperadmin"
      @click="openInvite"
      class="h-8 px-3 text-xs bg-emerald-600 text-white hover:bg-emerald-700 inline-flex items-center gap-1"
    >
      <Share2 class="w-4 h-4" />
      Convidar Licenciado
    </button>

    <!-- Verificar Carreira (somente licenciado) -->
    <button
      v-if="isLicensed"
      @click="verifyCareer"
      class="h-8 px-3 text-xs bg-amber-500 text-white hover:bg-amber-600 inline-flex items-center gap-1"
    >
      <RefreshCw class="w-4 h-4" />
      Verificar Carreira
    </button>

    <!-- Exportar / Imprimir -->
    <button
      @click="exportDashboard"
      class="h-8 px-3 text-xs bg-purple-600 text-white hover:bg-purple-700 inline-flex items-center gap-1"
    >
      <FileDown class="w-4 h-4" />
      <!-- Exportar -->
    </button>
    <button
      @click="printDashboard"
      class="h-8 px-3 text-xs bg-blue-600 text-white hover:bg-blue-700 inline-flex items-center gap-1"
    >
      <Printer class="w-4 h-4" />
      <!-- Imprimir -->
    </button>
    
    <!-- Botão Info: só aparece para Licenciado -->
    <button
      v-if="isLicensed"
      @click="showInfo=true"
      class="inline-flex items-center justify-center w-8 h-8 text-blue-600 hover:text-blue-700 border border-blue-200 hover:border-blue-300" 
      title="Informações sobre os cards"
    >
      <Info class="w-4 h-4" />
    </button>
  </div>

  <!-- Indicador de status do cadastro (lado direito) -->
  <div v-if="isLicensed && licensedStatus" class="ml-auto">
    <div class="h-8 px-3 text-xs inline-flex items-center gap-2 border rounded-full"
         :class="licensedStatus.pillClass">
      <span class="w-2 h-2 rounded-full" :class="licensedStatus.dotClass"></span>
      <span>Cadastro: {{ licensedStatus.label }}</span>
    </div>
  </div>

    <!-- Modal de Convite -->
    <Modal v-model="showInvite" :header-blue="true" :no-header-border="true">
      <template #title>Convidar Licenciado</template>
      <div class="space-y-4">
        <div class="text-sm text-gray-700">
          Compartilhe o link de cadastro com seu indicado. Escolha o canal abaixo.
        </div>
        <div class="flex items-center gap-4">
          <label class="inline-flex items-center gap-2 text-sm">
            <input type="radio" value="whatsapp" v-model="inviteChannel" /> WhatsApp
          </label>
          <label class="inline-flex items-center gap-2 text-sm">
            <input type="radio" value="email" v-model="inviteChannel" /> E-mail
          </label>
        </div>

        <div v-if="inviteChannel==='email'" class="flex items-center gap-2">
          <input v-model.trim="inviteEmail" type="email" placeholder="email@exemplo.com" class="flex-1 border rounded px-3 py-2 text-sm" />
          <button @click="sendInviteEmail" :disabled="!inviteEmail" class="px-3 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm disabled:opacity-50">Enviar</button>
        </div>

        <div v-else class="flex items-center gap-2">
          <button @click="shareWhatsApp" class="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Compartilhar no WhatsApp</button>
        </div>

        <div class="text-xs text-gray-500">
          Link: <span class="underline break-all">{{ inviteLink }}</span>
        </div>
      </div>
    </Modal>
    <!-- Modal de Aviso Genérico -->
    <Modal v-model="showNotice" :header-blue="true" :no-header-border="true">
      <template #title>Aviso</template>
      <div class="w-[520px] max-w-[90vw] p-1 text-sm">
        <div class="text-gray-800">{{ noticeMessage }}</div>
      </div>
      <template #footer>
        <div class="flex items-center justify-end gap-2 py-2">
          <button class="px-4 py-2 rounded border" @click="showNotice=false">Fechar</button>
        </div>
      </template>
    </Modal>
    <!-- Modal Resultado da Verificação de Carreira -->
    <Modal v-model="showCareerModal" :header-blue="true" :no-header-border="true">
      <template #title>Verificação de Carreira</template>
      <div class="w-[520px] max-w-[90vw] p-1 text-sm">
        <div v-if="careerResult?.updated" class="space-y-2">
          <div class="text-emerald-700 font-semibold">Parabéns! Você evoluiu de carreira.</div>
          <div class="flex items-center gap-2">
            <span class="text-gray-600">Antes:</span>
            <span class="px-2 py-0.5 rounded bg-gray-100 text-gray-800 text-xs">{{ careerResult?.before || '-' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-gray-600">Agora:</span>
            <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs">{{ careerResult?.after || '-' }}</span>
          </div>
        </div>
        <div v-else class="space-y-2">
          <div class="text-amber-700 font-semibold">Você ainda não atingiu os requisitos mínimos para subir para o próximo nível.</div>
          <div v-if="careerResult?.next?.stage_name" class="text-gray-700">Próximo nível: <b>{{ careerResult.next.stage_name }}</b></div>
          <ul class="list-disc ml-5 text-gray-700">
            <li v-if="typeof careerResult?.missing?.points === 'number'">Faltam {{ careerResult.missing.points }} pontos</li>
            <li v-if="typeof careerResult?.missing?.directs === 'number'">Faltam {{ careerResult.missing.directs }} diretos</li>
            <li v-if="typeof careerResult?.missing?.sales === 'number'">Faltam {{ careerResult.missing.sales }} vendas de usina</li>
          </ul>
          <div class="text-gray-600 text-xs">Não desista, você está quase lá!</div>
        </div>
      </div>
      <template #footer>
        <div class="flex items-center justify-end gap-2 py-2">
          <button class="px-4 py-2 rounded border" @click="showCareerModal=false">Fechar</button>
        </div>
      </template>
    </Modal>
    <!-- Modal de Cadastro -->
    <Modal v-model="showNew" :header-blue="true" :no-header-border="true">
      <template #title>Novo Licenciado</template>
      <FormPreRegister :key="preFormKey" ref="preForm" :in-modal="true" @close="showNew=false" @completed="preFormCompleted=true" />
      <template #footer>
        <div class="flex items-center justify-end gap-2 py-2">
          <button class="px-4 py-2 rounded border" @click="showNew=false">Fechar</button>
          <button form="preRegisterForm" type="submit" class="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white">Gravar</button>
        </div>
      </template>
    </Modal>

    <!-- Modal Info - Explicação dos Cards -->
    <Modal v-model="showInfo" :header-blue="true" :no-header-border="true">
      <template #title>Informações sobre os Cards</template>
      <div class="w-[600px] max-w-[90vw] p-1 text-sm leading-6">
        <div class="space-y-4">
          <div class="flex items-start gap-3">
            <Users class="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Rede</h4>
              <p class="text-gray-600">Mostra o total de pessoas na sua rede (incluindo você) e quantos são seus diretos (pessoas que você indicou diretamente).</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <Users class="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Usinas Vendidas</h4>
              <p class="text-gray-600">Quantidade de usinas fotovoltaicas que você vendeu e que foram aprovadas.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <DollarSign class="w-5 h-5 text-green-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Projeção de Bônus</h4>
              <p class="text-gray-600">Valor estimado de bônus que você receberá no mês, baseado nos pontos pendentes (R$ 0,10 por ponto).</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <Shield class="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Carreira Atual</h4>
              <p class="text-gray-600">Seu nível atual na carreira (Bronze, Prata, Ouro, Platina, Diamante). A cor do escudo muda conforme o nível.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <Target class="w-5 h-5 text-orange-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Pontos Projetados</h4>
              <p class="text-gray-600">Total de pontos que você tem pendentes (ainda não consolidados). Estes pontos geram bônus quando consolidados.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <CheckCircle2 class="w-5 h-5 text-emerald-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Pontos Consolidados</h4>
              <p class="text-gray-600">Total de pontos já consolidados (validados). Estes pontos já geraram bônus e estão no seu saldo.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <DollarSign class="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Saldo Disponível</h4>
              <p class="text-gray-600">Valor total disponível para saque na sua conta virtual. Este valor já foi consolidado e pode ser sacado.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-3">
            <FileText class="w-5 h-5 text-gray-600 mt-1 flex-shrink-0" />
            <div>
              <h4 class="font-semibold text-gray-800">Documentação</h4>
              <p class="text-gray-600">Status da sua documentação (Pendente, Aprovado, Reprovado). Deve estar aprovada para ativação.</p>
            </div>
          </div>
          
          <hr class="border-gray-200" />
          
          <div class="bg-blue-50 p-3 rounded-lg">
            <h4 class="font-semibold text-blue-800 mb-2">Regras para Saque</h4>
            <p class="text-blue-700 text-xs">
              O saque está disponível conforme as configurações gerais do sistema. 
              Consulte as configurações para ver os valores mínimos e prazos estabelecidos.
            </p>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</div>
<!-- Barra de boas-vindas -->
<div>
  <div class="rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white p-5">
    <div class="flex items-center justify-between">
      <div>
        <div class="text-2xl font-bold">Bem-vindo de volta, {{ auth.user?.username }}! 👋</div>
        <div class="text-sm opacity-90">Aqui está um resumo do seu desempenho hoje</div>
      </div>
      <div class="flex items-center gap-2 flex-wrap justify-end">
        <!-- Carreira Atual no header -->
        <div class="h-8 px-3 text-xs bg-white/20 hover:bg-white/30 text-white rounded-full inline-flex items-center gap-2">
          <Shield class="w-4 h-4" :class="careerIconClass" />
          <span class="opacity-90">Carreira Atual:</span>
          <span class="font-semibold">{{ careerValue }}</span>
        </div>

        <!-- Resumo compacto da Assinatura (licenciado) -->
        <template v-if="isLicensed">
          <div class="h-8 px-3 text-xs bg-white/15 text-white rounded-full inline-flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-blue-300"></span>
            <span class="opacity-90">Plano:</span>
            <span class="font-semibold truncate max-w-[140px]">{{ subscription.plan_name || '-' }}</span>
          </div>
          <div class="h-8 px-3 text-xs bg-white/15 text-white rounded-full inline-flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-300"></span>
            <span class="opacity-90">Ativo desde</span>
            <span class="font-semibold">{{ formatDate(subscription.dtt_activation) }}</span>
          </div>
          <div class="h-8 px-3 text-xs bg-white/15 text-white rounded-full inline-flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-orange-300"></span>
            <span class="opacity-90">Expira</span>
            <span class="font-semibold">{{ formatDate(subscription.expires_at) }}</span>
          </div>
          
        </template>
      </div>
    </div>
  </div>
</div>

<div class="flex">
    <div class="flex-1">
    <main ref="dashboardRef" class="pt-4 pr-4 pb-6 pl-4 space-y-6 relative">
    
    <!-- Accordion de Alertas -->
    <div v-if="alertsCount > 0" class="rounded-lg border bg-white/70 shadow-sm">
      <button @click="alertsOpen = !alertsOpen" class="w-full flex items-center justify-between px-3 py-2">
        <div class="flex items-center gap-2">
          <BellRing class="w-5 h-5 text-amber-600" />
          <span class="font-semibold text-gray-800">Você tem mensagens importantes</span>
          <span class="ml-2 px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-800 border border-amber-200">{{ alertsCount }}</span>
        </div>
        <ChevronDown class="w-4 h-4 text-gray-500" :class="alertsOpen ? '' : '-rotate-90'" />
      </button>
      <div v-show="alertsOpen" class="px-3 pb-3 space-y-2">
        <!-- Contrato pendente -->
        <div v-if="subscription.contract_status && subscription.contract_status !== 'signed'" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
            <div>
              <div class="font-semibold text-amber-800">Contrato de adesão pendente.</div>
              <div class="text-amber-800/80 text-sm">Reenvie o contrato para seu e‑mail para assinar eletronicamente.</div>
            </div>
          </div>
          <div>
            <button @click="resendContract" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Reenviar Contrato</button>
          </div>
        </div>
        <!-- Documentos PF -->
        <div v-if="isLicensed && documents && documents.pf && documents.pf !== 'approved'" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
            <div>
              <div class="font-semibold text-amber-800">Atenção: você ainda não concluiu o envio de sua documentação pessoal.</div>
              <div class="text-amber-800/80 text-sm">Conclua o envio e aguarde aprovação para ativação completa.</div>
            </div>
          </div>
          <div>
            <button @click="router.push('/documents')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Enviar Documentos</button>
          </div>
        </div>
        <!-- Documentos PJ -->
        <div v-if="isLicensed && documents && Array.isArray(documents.company_cnpjs) && documents.company_cnpjs.length && documents.pj && documents.pj !== 'approved'" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
            <div>
              <div class="font-semibold text-amber-800">Você ainda não enviou sua documentação referente à sua empresa de CNPJ {{ maskCnpj(documents.company_cnpjs[0]) }}.</div>
              <div class="text-amber-800/80 text-sm">Anexe os documentos obrigatórios para aprovação.</div>
            </div>
          </div>
          <div>
            <button @click="router.push('/company')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Enviar Documentos</button>
          </div>
        </div>
        <!-- Pagamento pendente -->
        <div v-if="billing.pending_annual_payment" class="p-4 bg-amber-50 border border-amber-200 rounded flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0"></div>
            <div>
              <div class="font-semibold text-amber-800">Pagamento do Plano Anual pendente</div>
              <div class="text-amber-800/80 text-sm">Conclua o pagamento para ativar e manter seus benefícios na rede.</div>
            </div>
          </div>
          <div>
            <button @click="openPayment" class="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Pagar Agora</button>
          </div>
        </div>
        <!-- Operador: documentos pendentes -->
        <div v-if="isOperator && pendingDocumentsCount > 0" class="p-4 bg-blue-50 border border-blue-200 rounded flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0"></div>
            <div>
              <div class="font-semibold text-blue-800">
                {{ pendingDocumentsCount }} {{ pendingDocumentsCount === 1 ? 'documento' : 'documentos' }} pendente{{ pendingDocumentsCount === 1 ? '' : 's' }} de revisão
              </div>
              <div class="text-blue-800/80 text-sm">Há documentos de licenciados aguardando sua revisão e aprovação.</div>
            </div>
          </div>
          <div>
            <button @click="router.push('/documents/review')" class="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm">Revisar Documentos</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cards principais -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card v-for="(c, idx) in orderedCards" :key="c.key" :className="cardClass(c, idx)" :iconBgClass="iconBgFor(c)" :descriptionClass="descriptionClass" @click="c.route && router.push(c.route)" class="cursor-pointer">
         <template #title><div>{{ displayTitle(c) }}</div></template>
         <template #content>
           <div>
              <template v-if="c.key === 'docs_status'">
                <div class="text-sm leading-5">
                  <div class="flex items-center gap-2">
                    <span :class="dotClassFor(c.value?.pf)" class="inline-block w-2.5 h-2.5 rounded-full"></span>
                    <span>PF: {{ statusLabel(c.value?.pf) }}</span>
                  </div>
                  <div class="flex items-center gap-2 mt-1">
                    <span :class="dotClassFor(c.value?.pj)" class="inline-block w-2.5 h-2.5 rounded-full"></span>
                    <span>PJ: {{ statusLabel(c.value?.pj) }}</span>
                  </div>
                </div>
              </template>
             <template v-else>
               <p class="text-2xl font-bold">{{ displayValue(c) }}</p>
             </template>
           </div>
         </template>
         <template #description><div v-if="c.delta">{{ c.delta }}</div></template>
         <template #icon><component :is="iconFor(c)" class="w-7 h-7" /></template>
      </Card>
    </div>

  <!-- Ações rápidas, relatórios e configurações -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Ações Rápidas -->
          <div class="border p-6 rounded-lg bg-white shadow-sm">
            <h2 class="font-bold text-lg mb-1">Ações Rápidas</h2>
            <p class="text-gray-600 text-sm mb-4">Gerencie o sistema rapidamente</p>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div 
                v-for="qa in quickActions" 
                :key="qa.route" 
                @click="router.push(qa.route)" 
                class="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors group"
              >
                <component :is="iconForQuickAction(qa)" class="w-8 h-8 mb-2 text-blue-600 group-hover:text-blue-700" />
                <span class="text-sm font-medium text-center text-gray-700 group-hover:text-gray-900">{{ qa.label }}</span>
              </div>
            </div>
          </div>

          <!-- Relatórios -->
          <div class="border p-6 rounded-lg bg-white shadow-sm">
            <h2 class="font-bold text-lg mb-1">Relatórios</h2>
            <p class="text-gray-600 text-sm mb-4">Acesse relatórios e análises</p>
            <div class="grid grid-cols-3 gap-3">
              <!-- Relatório Geral -->
              <div 
                @click="router.push('/reports/general')" 
                class="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors group"
              >
                <BarChart3 class="w-8 h-8 mb-2 text-green-600 group-hover:text-green-700" />
                <span class="text-sm font-medium text-center text-gray-700 group-hover:text-gray-900">Geral</span>
              </div>
              <!-- Relatório de Pontos -->
              <div 
                @click="router.push('/reports/points')" 
                class="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors group"
              >
                <Target class="w-8 h-8 mb-2 text-green-600 group-hover:text-green-700" />
                <span class="text-sm font-medium text-center text-gray-700 group-hover:text-gray-900">Pontos</span>
              </div>
              <!-- Relatório de Bônus -->
              <div 
                @click="router.push('/reports/bonus')" 
                class="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors group"
              >
                <DollarSign class="w-8 h-8 mb-2 text-green-600 group-hover:text-green-700" />
                <span class="text-sm font-medium text-center text-gray-700 group-hover:text-gray-900">Bônus</span>
              </div>
              <!-- Relatório de Fechamentos -->
              <div 
                @click="router.push('/reports/closures')" 
                class="flex flex-col items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors group col-span-3 sm:col-span-1"
              >
                <FileText class="w-8 h-8 mb-2 text-green-600 group-hover:text-green-700" />
                <span class="text-sm font-medium text-center text-gray-700 group-hover:text-gray-900">Fechamentos</span>
              </div>
            </div>
          </div>

          <!-- Distribuição Geográfica (sem borda/títulos) -->
          <div class="p-0 rounded-lg bg-white shadow-sm">
            <BrazilStatesMap @select="openUfTotals" />
          </div>
        </div>

        

        <!-- Resumo Operacional -->
        <div v-if="!isLicensed" class="bg-white border rounded-lg p-6 shadow-sm">
          <h2 class="font-bold text-lg mb-6">Resumo Operacional</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Pontos Gerados 
            <div class="text-center">
              <div class="text-3xl font-bold text-blue-600 mb-1">{{ summary.points_generated || 0 }}</div>
              <div class="text-sm text-gray-500">Pontos Gerados</div>
            </div>-->
            
            <!-- Pré-Cadastros -->
            <div class="text-center">
              <div class="text-3xl font-bold text-green-600 mb-1">{{ summary.pre_registers || 0 }}</div>
              <div class="text-sm text-gray-500">Pré-Cadastros (30 dias)</div>
            </div>
            
            <!-- Ativações -->
            <div class="text-center">
              <div class="text-3xl font-bold text-purple-600 mb-1">{{ summary.activations || 0 }}</div>
              <div class="text-sm text-gray-500">Ativações</div>
            </div>
            
            <!-- Solicitações de Saque -->
            <div class="text-center">
              <div class="text-3xl font-bold text-orange-600 mb-1">{{ summary.withdraw_requests || 0 }}</div>
              <div class="text-sm text-gray-500">Solicitações de Saque</div>
            </div>
          </div>
        </div>

        <!-- Modal UF -->
        <Modal v-model="showUf" :header-blue="true" :no-header-border="true">
          <template #title>Totais por Estado — {{ uf }}</template>
          <div style="margin-top:10px; position: relative; min-height: 80px;">
            <LoadingOverlay v-if="ufLoading" :fullscreen="false" message="Carregando..." />
            <div v-else class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <Card v-for="c in ufCards" :key="c.key">
                  <template #title><div>{{ c.title }}</div></template>
                  <template #content><div><p class="text-xl font-bold">{{ c.value }}</p></div></template>
                </Card>
              </div>
              <div class="border p-3 rounded text-sm">
                <div class="font-semibold mb-2">Resumo</div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <div><span class="text-gray-500">Pré-Cadastros (30d): </span><span class="font-medium">{{ ufSummary.pre_registers || 0 }}</span></div>
                  <div><span class="text-gray-500">Ativações: </span><span class="font-medium">{{ ufSummary.activations || 0 }}</span></div>
                  <div><span class="text-gray-500">Solicitações de Saque: </span><span class="font-medium">{{ ufSummary.withdraw_requests || 0 }}</span></div>
                </div>
              </div>
            </div>
          </div>
          <template #footer>
            <div class="flex items-center justify-end gap-2 py-2">
              <button class="px-4 py-2 rounded border" @click="showUf=false">Fechar</button>
            </div>
          </template>
        </Modal>
        <!-- Overlay global para ações longas (exportar/imprimir) -->
        <LoadingOverlay v-if="actionLoading" :fullscreen="true" message="Processando..." />
      </main>
    </div>
  </div>
  
</div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { computed, ref, onMounted, watch } from 'vue'
import Card from '@/components/ui/Card.vue'
import { UserPlus, DollarSign, TrendingUp, Users, FileText, Plus, Share2, FileDown, Printer, CheckCircle2, Clock, XCircle, AlertTriangle, Settings, BarChart3, Network, Target, Shield, Info, RefreshCw, BellRing, ChevronDown } from 'lucide-vue-next'
import api from '@/services/axios'
import Modal from '@/components/ui/Modal.vue'
import Button from '@/components/ui/Button.vue'
import FormPreRegister from '@/components/FormPreRegister.vue'
import BrazilStatesMap from '@/components/BrazilStatesMap.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'

const auth = useAuthStore()
const router = useRouter()
const showNew = ref(false)
const showInfo = ref(false)
const preForm = ref(null)
const preFormKey = ref(0)
const dashboardRef = ref(null)
const actionLoading = ref(false)
const preFormCompleted = ref(false)
const showCareerModal = ref(false)
const careerResult = ref(null)
const showNotice = ref(false)
const noticeMessage = ref('')

// Exemplo: se você salva grupos no `auth.user`
const isLicensed = computed(() => auth.user?.groups?.includes('Licenciado'))
const isSuperadmin = computed(() => auth.user?.is_superuser || auth.user?.groups?.includes('Superadmin'))
const isOperator = computed(() => auth.user?.groups?.includes('Operador') || auth.user?.is_staff || auth.user?.is_superuser)

// abre modal de cadastro pelo botão acima (showNew=true)

const cards = ref([])
const quickActions = ref([])
const billing = ref({ pending_annual_payment: false, payment_link_url: null, adesion_id: null })
const documents = ref({ pending: false, status: 'pending' })
const summary = ref({ pre_registers: 0, activations: 0, withdraw_requests: 0 })
const subscription = ref({ plan_name: null, dtt_record: null, dtt_activation: null, expires_at: null, contract_status: 'pending' })
const pendingDocumentsCount = ref(0)
const alertsOpen = ref(true)

// Valor da carreira atual (derivado dos cards quando presente)
const careerValue = computed(() => {
  const found = (cards.value || []).find(c => c.key === 'career')
  const val = (found?.value || '').toString().trim()
  if (!val || val === '-' || val.toLowerCase() === 'none') return 'Nenhuma'
  return val
})

const careerIconClass = computed(() => {
  const raw = (cards.value || []).find(c => c.key === 'career')?.value || ''
  const v = raw.toString().toLowerCase()
  if (v.includes('bronze')) return 'text-amber-200'
  if (v.includes('prata') || v.includes('silver')) return 'text-gray-200'
  if (v.includes('ouro') || v.includes('gold')) return 'text-yellow-200'
  if (v.includes('platina') || v.includes('platinum')) return 'text-blue-200'
  if (v.includes('diamante') || v.includes('diamond')) return 'text-purple-200'
  return 'text-gray-200'
})
const contractPillClass = computed(() => (
  subscription.value?.contract_status === 'signed'
    ? 'bg-emerald-500/20 text-emerald-50'
    : 'bg-amber-500/20 text-amber-50'
))
const contractDotClass = computed(() => (
  subscription.value?.contract_status === 'signed'
    ? 'bg-emerald-300'
    : 'bg-amber-300'
))
// Ordenação preferencial de cards por perfil
const orderLicensed = [
  'network',
  'sold_plants',
  'bonus_projection',
  // 'career' removido do grid (exibido no header)
  'points_projected',
  'points_consolidated',
  'balance_available',
  'docs_status',
]
const orderDefault = [
  'total_licensed',
  'active_affiliates',
  'roots_count',
  'network_edges',
  'operator_paid_adesions',
  'operator_paid_plants',
  'operator_bonus_total',
  'operator_points_total',
]

const orderedCards = computed(() => {
  const list = Array.isArray(cards.value) ? [...cards.value] : []
  // Remove o card de carreira do grid na visão do licenciado (está no header)
  const filtered = isLicensed.value ? list.filter(c => c?.key !== 'career') : list
  const baseOrder = isLicensed.value ? orderLicensed : orderDefault
  const priority = new Map(baseOrder.map((k, i) => [k, i]))
  return filtered.sort((a, b) => {
    const ai = priority.has(a?.key) ? priority.get(a.key) : 1000 + (a?.order || 0)
    const bi = priority.has(b?.key) ? priority.get(b.key) : 1000 + (b?.order || 0)
    if (ai !== bi) return ai - bi
    return (a?.title || '').localeCompare(b?.title || '')
  })
})

// Cards sem Documentação (removido do grid)
const cardsWithoutDocs = computed(() => orderedCards.value.filter(c => c.key !== 'docs_status'))


// Mapeia status do cadastro/licença do usuário
const licensedStatus = computed(() => {
  // Preferência: status vindo do dashboard -> documents.status
  const st = (documents.value?.status || '').toLowerCase()
  // Fallback simples por enquanto: se não houver status, mostra pendente quando houver documentos pendentes ou pagamento pendente
  if (st === 'approved' || st === 'ativo' || st === 'active') {
    return { label: 'Ativo', pillClass: 'bg-emerald-50 border-emerald-200 text-emerald-700', dotClass: 'bg-emerald-500', icon: CheckCircle2 }
  }
  if (st === 'pending' || st === 'aguardando' || documents.value?.pending) {
    return { label: 'Em validação', pillClass: 'bg-blue-50 border-blue-200 text-blue-700', dotClass: 'bg-blue-500', icon: Clock }
  }
  if (st === 'rejected' || st === 'reprovado') {
    return { label: 'Reprovado', pillClass: 'bg-red-50 border-red-200 text-red-700', dotClass: 'bg-red-500', icon: XCircle }
  }
  if (billing.value?.pending_annual_payment) {
    return { label: 'Pagamento pendente', pillClass: 'bg-amber-50 border-amber-200 text-amber-700', dotClass: 'bg-amber-500', icon: AlertTriangle }
  }
  return { label: 'Em validação', pillClass: 'bg-blue-50 border-blue-200 text-blue-700', dotClass: 'bg-blue-500', icon: Clock }
})

async function fetchDashboard() {
  const { data } = await api.get('/api/core/dashboard/')
  cards.value = data?.cards || []
  quickActions.value = data?.quickActions || []
  billing.value = data?.billing || { pending_annual_payment: false }
  documents.value = data?.documents || { pending: false, status: 'pending' }
  summary.value = data?.summary || { pre_registers: 0, activations: 0, withdraw_requests: 0 }
  subscription.value = data?.subscription || subscription.value
  
  // Buscar count de documentos pendentes se for operador
  if (isOperator.value) {
    try {
      const { data: countData } = await api.get('/api/core/pending-documents-count/')
      pendingDocumentsCount.value = countData?.count || 0
    } catch (error) {
      console.error('Erro ao buscar documentos pendentes:', error)
      pendingDocumentsCount.value = 0
    }
  }
}

onMounted(fetchDashboard)

function cardClass(card, index) {
  const base = 'bg-gradient-to-r text-white shadow-sm hover:scale-[1.01] transition-transform'
  const byKey = {
    total_licensed: 'from-purple-400 to-purple-500',
    active_affiliates: 'from-emerald-400 to-emerald-500',
    roots_count: 'from-purple-400 to-purple-500',
    network_edges: 'from-orange-300 to-orange-400',
    directs: 'from-purple-400 to-purple-500',
    team_size: 'from-purple-400 to-purple-500',
    active_team: 'from-emerald-400 to-emerald-500',
    career: 'from-orange-300 to-orange-400',
    // Documentação com cinza mais consistente (menos branco)
    docs_status: 'from-gray-400 to-gray-600',
    operator_paid_adesions: 'from-emerald-400 to-emerald-500',
    operator_paid_plants: 'from-blue-400 to-blue-500',
    operator_bonus_total: 'from-purple-400 to-purple-500',
    operator_points_total: 'from-orange-300 to-orange-400',
    bonus_projection: 'from-purple-400 to-purple-500',
    points_projected: 'from-emerald-400 to-emerald-500',
    points_consolidated: 'from-emerald-400 to-emerald-500',
    balance_available: 'from-emerald-400 to-emerald-500',
    network: 'from-purple-400 to-purple-500',
    sold_plants: 'from-amber-300 to-amber-400',
  }
  const palette = [
    'from-purple-400 to-purple-500',
    'from-emerald-400 to-emerald-500',
    'from-blue-400 to-blue-500',
    'from-orange-300 to-orange-400',
  ]
  const grad = byKey[card?.key] || palette[index % palette.length]
  return `${base} ${grad}`
}

function iconFor(card) {
  const key = card?.key
  switch (key) {
    case 'directs':
      return UserPlus
    case 'team_size':
      return Users
    case 'bonus_projection':
      return DollarSign
    case 'points_projected':
      return Target
    case 'points_consolidated':
      return CheckCircle2
    case 'balance_available':
      return DollarSign
    case 'network':
      return Users
    case 'sold_plants':
      return Users
    case 'career':
      return Shield
    case 'docs_status':
      return FileText
    case 'operator_paid_adesions':
      return DollarSign
    case 'operator_paid_plants':
      return Users
    case 'operator_bonus_total':
      return DollarSign
    default:
      return Users
  }
}

function iconBgFor(card) {
  const key = card?.key
  if (key === 'sold_plants') {
    return 'bg-amber-100/30'
  }
  if (key === 'docs_status') {
    return 'bg-white/10'
  }
  return 'bg-white/40'
}

function displayValue(card) {
  const monetaryKeys = new Set(['bonus_projection', 'balance_available'])
  if (monetaryKeys.has(card?.key) && typeof card?.value === 'number') {
    try {
      return card.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
    } catch (_) {
      return `R$ ${Number(card.value).toFixed(2)}`
    }
  }
  // Card de documentação: exibir PF/PJ em linhas
  if ((card?.key || '') === 'docs_status') {
    // Conteúdo customizado é renderizado acima
    return ''
  }
  return card?.value
}

function statusLabel(raw) {
  const v = (raw || '').toString().toLowerCase()
  const map = { approved: 'Aprovado', pending: 'Pendente', rejected: 'Reprovado', awaiting: 'Aguardando', incomplete: 'Incompleto' }
  return map[v] || (raw || '-')
}

function dotClassFor(raw) {
  const v = (raw || '').toString().toLowerCase()
  if (v === 'approved') return 'bg-emerald-400'
  if (v === 'pending' || v === 'incomplete') return 'bg-amber-400'
  if (v === 'awaiting') return 'bg-blue-400'
  // não enviado/reprovado
  return 'bg-rose-400'
}

function displayTitle(card) {
  if ((card?.key || '') === 'network') return 'Pessoas na Rede'
  return card?.title
}

function formatDate(iso) {
  if (!iso) return '-'
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('pt-BR')
  } catch (_) {
    return '-'
  }
}

function iconForQuickAction(action) {
  const key = action?.key || action?.route || ''
  if (key.includes('network') || key.includes('tree') || key.includes('rede')) {
    return Network
  }
  if (key.includes('report') || key.includes('relatorio')) {
    return BarChart3
  }
  if (key.includes('settings') || key.includes('config')) {
    return Settings
  }
  if (key.includes('licensed') || key.includes('afiliado') || key.includes('licenciado')) {
    return Users
  }
  return Settings
}

const alertsCount = computed(() => {
  let count = 0
  if (subscription.value?.contract_status && subscription.value.contract_status !== 'signed') count++
  if (isLicensed.value && documents.value?.pf && documents.value.pf !== 'approved') count++
  if (isLicensed.value && Array.isArray(documents.value?.company_cnpjs) && documents.value.company_cnpjs.length && documents.value?.pj && documents.value.pj !== 'approved') count++
  if (isOperator.value && pendingDocumentsCount.value > 0) count++
  if (billing.value?.pending_annual_payment) count++
  return count
})

// Expor contador global no header (via localStorage) para o App/Header
watch(alertsCount, (n) => {
  try { localStorage.setItem('alertsCount', String(n || 0)) } catch {}
})
function openPayment() {
  const adesionId = billing.value?.adesion_id
  if (!adesionId) return router.push('/network/adesions')
  router.push({ path: '/payment', query: { adesion: adesionId } })
}

// Modal Totais por UF
const showUf = ref(false)
const ufLoading = ref(false)
const uf = ref('')
const ufCards = ref([])
const ufSummary = ref({})

async function openUfTotals(ufCode) {
  uf.value = ufCode
  ufLoading.value = true
  try {
    const { data } = await api.get(`/api/core/dashboard/?state=${encodeURIComponent(ufCode)}`)
    ufCards.value = data?.cards || []
    ufSummary.value = data?.summary || {}
  } catch (e) {
    ufCards.value = []
    ufSummary.value = {}
  } finally {
    ufLoading.value = false
    showUf.value = true
  }
}

// Convite de licenciado
const showInvite = ref(false)
const inviteChannel = ref('whatsapp')
const inviteEmail = ref('')
const inviteLink = computed(() => {
  const origin = window.location.origin
  const username = auth.user?.username || ''
  return `${origin}/preRegister?ind=${encodeURIComponent(username)}`
})

function openInvite() {
  inviteChannel.value = 'whatsapp'
  inviteEmail.value = ''
  showInvite.value = true
}

function maskCnpj(v) {
  try {
    const s = String(v || '').padStart(14, '0').slice(-14)
    return `${s.slice(0,2)}.${s.slice(2,5)}.${s.slice(5,8)}/${s.slice(8,12)}-${s.slice(12,14)}`
  } catch { return v }
}

function shareWhatsApp() {
  const text = `Olá! Segue meu link para se cadastrar na FazEnergy: ${inviteLink.value}`
  if (navigator.share) {
    navigator.share({ title: 'Convite FazEnergy', text, url: inviteLink.value }).catch(()=>{})
  } else {
    const url = `https://wa.me/?text=${encodeURIComponent(text)}`
    window.open(url, '_blank')
  }
}

function sendInviteEmail() {
  const subject = 'Convite para cadastro na FazEnergy'
  const body = `Olá!\n\nUse este link para se cadastrar: ${inviteLink.value}\n\nObrigado!`
  const mail = `mailto:${encodeURIComponent(inviteEmail.value)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  window.location.href = mail
}

function submitPreForm() {
  try {
    const formEl = document.getElementById('preRegisterForm')
    if (formEl && typeof formEl.requestSubmit === 'function') {
      formEl.requestSubmit()
    } else if (formEl) {
      formEl.submit()
    }
    // Oculta imediatamente o botão até receber o evento completed
    preFormCompleted.value = true
  } catch {}
}

// mantém comportamento simples: usamos submit do form

// Sempre resetar o formulário ao abrir o modal
watch(showNew, (val) => {
  if (val && preForm.value && preForm.value.resetForm) {
    preForm.value.resetForm()
  }
  if (val) {
    // força recriar o componente evitando preenchimento automático do navegador
    preFormKey.value++
    // tentativa adicional: limpa inputs email/senha após montar
    const clear = () => {
      const formEl = document.getElementById('preRegisterForm')
      if (!formEl) return
      formEl.querySelectorAll('#pre_email, #pre_password, #pre_confirm_password').forEach((el) => {
        try {
          // @ts-ignore
          el.value = ''
          el.dispatchEvent(new Event('input', { bubbles: true }))
        } catch {}
      })
    }
    setTimeout(clear, 0)
    setTimeout(clear, 100)
    setTimeout(clear, 300)
    preFormCompleted.value = false
  }
})

// Export/Print Dashboard
async function exportDashboard() {
  try {
    actionLoading.value = true
    const el = dashboardRef.value
    if (!el) return
    const { default: html2canvas } = await import('html2canvas')
    const { jsPDF } = await import('jspdf')
    const canvas = await html2canvas(el, { scale: 2, useCORS: true })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pageWidth
    const imgHeight = canvas.height * imgWidth / canvas.width
    let y = 0
    // Suporte a múltiplas páginas
    while (y < imgHeight) {
      pdf.addImage(imgData, 'PNG', 0, -y, imgWidth, imgHeight)
      y += pageHeight
      if (y < imgHeight) pdf.addPage()
    }
    pdf.save(`dashboard_${new Date().toISOString().slice(0,10)}.pdf`)
  } catch {} finally {
    actionLoading.value = false
  }
}

async function printDashboard() {
  try {
    actionLoading.value = true
    const el = dashboardRef.value
    if (!el) return
    const { default: html2canvas } = await import('html2canvas')
    const canvas = await html2canvas(el, { scale: 2, useCORS: true })
    const dataUrl = canvas.toDataURL('image/png')
    const win = window.open('', '_blank')
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8" />
      <title>Imprimir Dashboard</title>
      <style>body{margin:0} img{display:block; width:100%; height:auto}</style>
    </head><body onload="window.print(); setTimeout(()=>window.close(), 50)">
      <img src="${dataUrl}" />
    </body></html>`
    win.document.write(html)
    win.document.close()
  } catch {} finally {
    actionLoading.value = false
  }
}

function goToContracts() {
  router.push('/settings')
}

// Verificar carreira: chama API e atualiza header/cards
async function verifyCareer() {
  try {
    actionLoading.value = true
    const { data } = await api.post('/api/core/career/verify/')
    careerResult.value = data || {}
    showCareerModal.value = true
    // Recarrega dashboard para refletir carreira atualizada
    await fetchDashboard()
  } catch (e) {
  } finally {
    actionLoading.value = false
  }
}

// Reenviar contrato via Lexo
async function resendContract() {
  try {
    actionLoading.value = true
    const { data } = await api.post('/api/contracts/templates/resend-adesion/')
    const email = auth.user?.email || ''
    noticeMessage.value = `Contrato reenviado para o e‑mail ${email}.`
    showNotice.value = true
  } catch (e) {
    noticeMessage.value = 'Não foi possível reenviar o contrato.'
    showNotice.value = true
  } finally {
    actionLoading.value = false
  }
}
</script>
