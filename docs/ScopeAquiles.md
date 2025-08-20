# Scope Aquiles — FazEnergyFinal

Documento de contexto e escopo consolidado das alterações recentes (backend e frontend).

## Visão Geral
- Monorepo: Django 5 + DRF (backend) e Vue 3 + Vite (frontend).
- Autenticação: JWT. Execução preferencial via Docker.
- Objetivo de negócio: plataforma MMN unilevel com adesões, planos, carreira, integrações (Lexo, Pagar.me), rede e notificações.

## Frontend (Vue 3)
### Rede
- Tela “Adesões” em Rede
  - Rota: `/network/adesions` (roles: superadmin e operador).
  - Menu: item “Adesões” em REDE; item “Equipe” removido.
  - Listagem via `DataTable` com filtros, exportação XLS e impressão, seguindo padrão de “Rede Completa”.
  - Colunas ordenadas: ID, Plano, Licenciado (id-username), Tipo, Criação, Pagamento, Status Pag. (badges: Pendente, Confirmado, Cancelado).

### Configurações (Settings)
- Abas principais: Geral, Comissões, Gateway, Planos, Planos de Carreira, Notificações, Webhooks, APIs, Contratos.
- Removida a aba principal “SMTP” (foi movido para dentro de Notificações).

#### Planos
- Refatorado `PlansTab.vue` para padrão de grid com coluna Ações (ícone), ID, Status como última.

#### Planos de Carreira
- `CareerPlansTab.vue`: grid com Ações (ícone lápis), ID, Última Edição (login/data), Status em badge.
- Modal com header azul, botões “Fechar/Gravar”.

#### Notificações
- Nova estrutura em sub-abas internas:
  - SMTP: formulário para configuração de e-mail (servidor/porta/usuário/senha/SSL/TLS/remetente/destinatário de teste).
  - Templates: grid CRUD de templates com “Envio de Teste” por linha; modal com editor (rich/HTML code) alternável.

#### Gateway
- Sub-abas internas: “Config API” (token/URLs/ativo) e “Webhook” (token/user/password/secret). Botão Gravar em ambas.

#### Contratos
- Sub-abas internas: “Lexo API” (configuração) e “Templates de Contrato” (grid + modal).
- Modal de template:
  - Editor rich no campo Corpo, com altura ajustável.
  - Guia de Chaves em card lateral (toggle Mostrar/Esconder), altura ~300px.

### Componentes/UX
- Botões de edição padronizados (ícone lápis sólido azul, dimensões h-[27px] w-7).
- Badges de status unificados.
- `RichTextEditor.vue` e `CodeEditor.vue` adicionados (rich + monoespaçado), com props de tamanho.

## Backend (Django + DRF)
### Plans
- `PlanCareer` API
  - Serializer `PlanCareerSerializer`.
  - ViewSet `PlanCareerViewSet`.
  - Rota: `api/plans/plan-careers/` (CRUD autenticado).
- `PlanAdesionSerializer`: incluído `licensed_username` para exibir `id-username` no front.

### Notifications
- Modelos já existentes: `NotifyConfig`, `NotifyTemplate`.
- APIs adicionadas:
  - `api/notifications/config/` (GET retorna o primeiro registro; POST/PUT salvam).
  - `api/notifications/templates/` (CRUD de templates).
  - `POST api/notifications/templates/{id}/test/` (envio de e-mail de teste com base no template; usa config SMTP).

### Finance (Gateway)
- API `GatewayConfig`
  - Serializer/ViewSet/URL: `api/finance/gateway-config/`.
  - GET cria registro default caso não exista (para facilitar o preenchimento via UI).

### Contracts (Lexo)
- APIs
  - `api/contracts/config/` (singleton GET/POST/PUT de `ContractConfig`).
  - `api/contracts/templates/` (CRUD de `ContractTemplate`).
- Remoções
  - `ContractLog` removido do projeto (model/admin), migração criada e referências limpas em `contracts/services.py`.

### Network
- Admin: registrado `ScoreReference` (listagem, filtros, busca) em `network/admin.py`.

### Core
- `Licensed`
  - Removidos campos `previous_career` e `dtt_previous_career`.
  - Ajustes no método de qualificação para carreira atual.
  - Admin `LicensedAdmin` atualizado (sem carreira anterior, `fieldsets` e validações ajustados).

## Rotas/Endpoints (resumo)
- Plans: `api/plans/plan-careers/`
- Notifications: `api/notifications/config/`, `api/notifications/templates/`, `api/notifications/templates/{id}/test/`
- Finance: `api/finance/gateway-config/`
- Contracts: `api/contracts/config/`, `api/contracts/templates/`

## Migrações
- Contracts: deleção de `ContractLog`.
- Core: remoção de `Licensed.previous_career` e `Licensed.dtt_previous_career`.
- Plans/Notifications/Finance/Contracts: novas rotas/serializers/views sem alterações de esquema além das citadas.

## Pendências/Operação
- Executar migrações após alterações do backend:
  - `python manage.py migrate`
- Garantir token JWT válido para acessar rotas autenticadas no front.
- Opcional: integrar CKEditor 5/Monaco oficiais se necessário (dependências de build).

---
Atualizado por: Assistente (Aquiles) — data da última consolidação conforme execução das tarefas recentes.
