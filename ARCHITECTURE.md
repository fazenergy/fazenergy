# Arquitetura - FazEnergyFinal

## Visão Geral
- Monorepo com `@backend/` (Django + DRF) e `@frontend/` (Vue 3 + Vite).
- Comunicação via API REST JSON.
- Orquestração via Docker Compose (banco PostgreSQL, backend, frontend).

## Serviços (docker-compose)
- Banco: `postgres:15` exposto em `5432`.
- Backend: Django em `8000` (container `fazenergy-backend`).
- Frontend: Vite Dev Server em `5173` (container `fazenergy-frontend`).

## Backend (`@backend/`)
- Stack: Django 5, DRF, SimpleJWT, Celery, Redis (para filas), PostgreSQL.
- Admin: Jazzmin.
- Apps modulares (atuais): `core`, `contractor` (substitui `prospect`), `plans`, `contracts`, `finance`, `network`, `location`, `notifications`, `webhooks`.
- Arquivos relevantes:
  - `config/settings.py`, `config/urls.py`, `config/celery.py`.
- Uploads/estática: `MEDIA_URL`/`MEDIA_ROOT` e `static/`.

Rotas base (sujeitas a evoluções; conferir no código):
```9:27:backend/config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('core.urls')),
    path('api/core/', include('core.urls')),
    path('api/plans/', include('plans.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('core.urls')),  # ou o nome do seu app
    path('api/location/', include('location.urls')),
    path('api/contractor/', include('contractor.urls')),

    # Webhooks
    path('api/webhook/pagarme/', pagarme_webhook, name='webhook-pagarme'),
    #path('api/webhook/lexio/', lexio_webhook, name='webhook-lexio'),
    #path('api/webhook/lexio', lexio_webhook),  # para aceitar sem a barra também

    # Importante para Upload
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    
   


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### App contractor (integração REVO)
- Entidades: `Contractor`, `ContractorProposal`, `ContractorProposalResult`, `ContractorProposalLeadActor`.
- Endpoints principais:
  - `POST /api/contractor/revo/simulation/` → chama REVO e salva Proposal/Result/LeadActors
  - `GET /api/contractor/contractors/`, `GET /api/contractor/proposals/`, `GET /api/contractor/proposal-results/`
- Regras:
  - Anti-aliciamento e janela: bloqueia CPF+CEP com proposta ativa (409) e propostas expiradas nos últimos 30 dias com outro licenciado (409). `?override=1` apenas para staff.
  - Idempotência: se já houver proposta ativa para mesmo licenciado+CPF+CEP, retorna 409 com `proposal/result` existentes.
  - Lead Actors: `contractor` obrigatório; para PJ exige `legal_responsible`; quando `owner != "Próprio"`, exige `owner`.
  - Persistência: `ContractorProposal.request_payload` e `ContractorProposalResult.response_payload` (JSONB).
  - Efetivar (PUT): atualiza a simulação existente na REVO e o último `ContractorProposalResult` (não cria novo). Salva `response_payload_put`.
  - Campos relevantes:
    - ContractorProposal: endereço de instalação, consumo (`monthly_consumption`), `energy_provider_*`, `visit_1/visit_2`.
    - Contractor (managed=False, legado): identificação/contato; não guarda mais CEP nem preferências.
  - Retorno do endpoint (`POST /api/contractor/revo/simulation/`):
    - `{"revo": {…}, "proposal_id": <int>, "result_id": <int>, "proposal": {…}, "result": {…}}` (201 em sucesso)
    - `409` em conflitos (ativa/idempotente/recentes), com `licensed_id` e dados da proposta existente.

#### Efetivar Proposta (PUT)
- Entrada: `reference` da proposta simulada, `contract_duration`, `owner`, `installation_address`, e `lead_actors` conforme PF/PJ.
- Efeitos:
  - Atualiza `ContractorProposal` (endereço, `consumer_unit`, `consumer_group`, `energy_provider_*`).
  - Atualiza último `ContractorProposalResult` e persiste `response_payload_put`.
  - Upsert em `ContractorProposalLeadActor` para `owner`/`legal_responsible`. Se `owner == Próprio`, remove o registro de `owner`.

## Frontend (`@frontend/`)
- Stack: Vue 3, Vite, Tailwind CSS, Pinia, Vue Router, Axios.
- Estrutura:
  - `src/views` (páginas), `src/components` (componentes), `src/services` (APIs), `src/store` (estado), `src/router` (rotas), `src/config` (configs).
- Dev server: `http://localhost:5173`.

#### Propostas (UI atual)
- Página `src/views/Proposal/List.vue` centraliza listagem, simulação (modal) e resultado/efetivação (modal).
- Padrões de UI:
  - Fieldset/card: título “flutuante” sobre a borda (legend) em Dados Iniciais, Agendamento, Consumo Mensal, Atores, Planos disponíveis e Dados para Efetivação.
  - Cards informativos com `bg-slate-50`, borda `slate-200` e sombra leve (Última fatura, kWp, kWh anual, Área, Módulos, Plano escolhido).
  - Destaque do plano selecionado com `bg-emerald-50`, borda 2px `emerald-600` e `ring` sutil.
- Validações front:
  - Obrigatórios: proprietário, distribuidora, UC, grupo, 12 consumos, e-mail, CEP (8 dígitos), nome completo (PF) e CPF (PF).
  - Celular normalizado (apenas dígitos, máx. 11).
- Edição de visitas por PATCH em `Proposal` sem acionar REVO.

#### Refatoração planejada (pós-funcional)
- Extrair os modais para `SimulateModal.vue` e `ResultModal.vue` e subcomponentes reutilizáveis (`ActorsForm.vue`, `MonthlyConsumption.vue`, `PlanOptions.vue`, `FieldsetCard.vue`).

## Como rodar (Docker)
1) Configure `.env`