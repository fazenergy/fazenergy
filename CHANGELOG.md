# CHANGELOG

Todas as mudanças relevantes do projeto. Use datas no formato YYYY-MM-DD.

## 2025-09-08

### Backend (contractor)
- Revo PUT (Efetivar Proposta):
  - Atualiza o último `ContractorProposalResult` da proposta (não cria novo).
  - Persiste a resposta do PUT em `ContractorProposalResult.response_payload_put`.
  - Atualiza `ContractorProposal` com dados retornados/confirmados (endereço de instalação, `consumer_unit`, `consumer_group`, `energy_provider_*`).
  - Upsert de `ContractorProposalLeadActor` para `owner` e `legal_responsible`; remove `owner` quando `owner == "Próprio"`.
- POST (Simular): mantém validações de anti-aliciamento (CPF+CEP) e idempotência; salva `response_payload` do POST.
- Serialização:
  - `ProposalSerializer` inclui `contractor` embutido.
  - `ProposalViewSet`: suporte a listagem e detail para consumo no frontend.

### Frontend (Vue 3)
- Propostas (`src/views/Proposal/List.vue`):
  - Modal “Simular Proposta” (criação/edição) com validações e máscara/norm. de celular (máx. 11 dígitos, apenas números).
  - Modal “Resultado da Simulação” com fluxo de Efetivação integrado (PUT), montando `lead_actors` corretamente (PF/PJ/owner) e priorizando dados do banco.
  - Preenchimento automático de `licensed_id` para usuário licenciado.
  - “Editar Proposta”: apenas atualiza `visit_1/visit_2` (PATCH) sem chamar REVO.
  - UI/UX:
    - Padrão visual com fieldsets/cards (legend flutuante) nas seções: Dados Iniciais, Agendamento, Consumo Mensal, Atores, Planos disponíveis, Dados para Efetivação.
    - Cards informativos (Última fatura, kWp, kWh anual, Área, Módulos, Plano escolhido) com `bg-slate-50`, borda `slate-200` e sombra leve.
    - “Planos disponíveis”: destaque no plano selecionado (`bg-emerald-50`, borda 2px `emerald-600`, `ring` sutil, ícone de confirmação).
    - “Consumo mensal”: seção colapsável (Mostrar/Esconder) e nomes de meses por extenso.
    - Atores (simular/efetivar): três colunas com o mesmo padrão de cards; `owner` exibido só quando `owner === 'Outro'`.
  - Melhorias de acessibilidade e consistência de labels (text-[11px]) e altura de inputs (h-8 onde aplicável).

### Documentação
- `ARCHITECTURE.md`:
  - Documentado o fluxo de Efetivar Proposta (PUT) e persistências (`response_payload_put`).
  - Registrados padrões de UI e plano de refatoração pós-funcional (modais e subcomponentes reutilizáveis).
- `docs/SCOPE.md`:
  - Atualizadas mudanças recentes e regras de `lead_actors` (PF/PJ/owner).

### Observações de migração
- Certificar que as migrações referentes a `ContractorProposalResult.response_payload_put` foram aplicadas no container do backend.

---

## 2025-09-06 ~ 2025-09-07
- Correções de dependências no frontend (`html2canvas`, `jspdf`, `@svg-maps/brazil`).
- Ajustes de layout/validação no formulário de simulação (ordem de validação, asteriscos, bordas em campos obrigatórios e reset do modal).
