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

- Acordeon de alertas no Dashboard
  - Header do acordeon com sininho e contador de mensagens.
  - Agrupa múltiplos avisos (contrato pendente, documentos PF/PJ pendentes, pagamento pendente, pendências de revisão para Operador).
  - Cada alerta mantém CTA específico (ex.: Reenviar Contrato, Enviar Documentos, Pagar Agora, Revisar Documentos).
  - O mesmo contador aparece no sininho do header global; ao clicar, abre modal com mensagens importantes.

### Conta de Saque (Novo)
- Rota: `/finance/withdraw-accounts` (roles: licenciado, superadmin)
- Grid padrão listando contas do licenciado: ID, Titular (PF/PJ), Banco, Tipo, Agência, Conta, Padrão.
- Modal Cadastro/Edição:
  - PF/PJ: se PJ, selecionar empresa aprovada (`LicensedCompany.stt_validate='approved'`). Caso não exista, cadastrar em “Minhas Empresas” e validar documentos.
  - Campos: Banco (código/nome), Tipo (corrente/poupança/pagamento), Agência + dígito, Conta + dígito, Titular, CPF/CNPJ, marcar como Padrão.
- Regras: CRUD apenas das contas do próprio usuário; exclusão bloqueada se houver saque pendente vinculado.

#### Padrão de Grid (obrigatório em todas as telas)
- Breadcrumb global no cabeçalho principal (Header.vue), derivado da rota atual.
  - As telas de listagem não devem renderizar breadcrumb local duplicado.
- Toolbar superior SEM borda de contorno, com layout em linha e espaçamento compacto.
  - Botões à esquerda (compactos — h-8, text-xs, ícones 16px):
    - + Adicionar: verde (Plus), abre modal padrão da funcionalidade da tela
    - Exportar: roxo (FileDown), exporta XLS da visão filtrada
    - Imprimir: azul (Printer), gera impressão/PDF da visão filtrada
  - Filtros imediatamente após os botões (ex.: Plano, Cidade), em selects compactos (h-8).
  - Busca responsiva à direita:
    - Campo de texto com `flex-1` para ocupar todo o espaço restante, “empurrando” até a borda direita quando houver espaço
    - Botão Pesquisar com ícone de lupa azul (Search)
    - Botão Limpar com ícone de borracha cinza (Eraser)
- Layout do grid com rodapé/paginação fixo no rodapé do container:
  - Aplicar min-height responsivo (cálculo por viewport) para que o grid preencha a área útil e mantenha o footer visível, como em Rede > Diretos.
- Colunas: a primeira deve ser Ações; a segunda o ID da linha; a última também apresenta o ID quando aplicável.
- Páginas alvo para aplicar o padrão: Rede (Diretos, Rede Completa, Adesões) e todas as demais listagens do sistema.

### Meu PJ (Novo)
- Rota: `/company` (roles: licenciado, superadmin)
- Menu: item "Meu PJ" no grupo Geral do sidebar.
- Listagem (grid padrão) das empresas do licenciado com Ações (editar), ID, CNPJ, Razão Social, Status, ID final.
- Modal de Cadastro/Edição:
  - Campos: CNPJ, Razão Social, Nome Fantasia, IE, IM, CEP, Endereço, Número, Complemento, Bairro, Telefone, Observação.
  - Uploads obrigatórios: Cartão CNPJ e Contrato Social.
  - Status da empresa: pending/rejected/approved (aprovada quando os 2 documentos estiverem aprovados).
- Regras:
  - Cadastro PJ é opcional; licenciado pode ter 0..N empresas (vários CNPJs).
  - Se cadastrar empresa, os 2 documentos PJ tornam-se obrigatórios e ficam pendentes até validação por Operador.
  - Tela de Revisão de Documentos permite filtrar por `owner_type` (PF/PJ) e exibe colunas Origem e Empresa.

### Fechamentos — Solicitação de Saque (Novo)
- Rota: `/reports/closures`
- Para Licenciado:
  - Botão “Solicitar Saque” com seleção de conta e valor (preenchimento automático dos dados da conta e validações de saldo/mínimo).
  - Seção “Solicitações de Saque” com status, previsão de recebimento e botão de cancelar quando pendente/agendado.
  - Ícone de histórico por linha mostrando todos os eventos desde a solicitação.
- Para Operador/Superadmin:
  - Ações por linha: Aprovar (define `expected_payout_date`), Agendar (define `scheduled_for` e previsão), Liberação de Emergência (motivo obrigatório; chama pagamento imediato), Cancelar.
  - Histórico abre modal com trilha completa (quem aprovou, motivo de emergência, cancelamento).
- Status exibidos: `pending`, `scheduled`, `processing`, `paid`, `canceled`, `rejected`.

### Dashboard — Mapa por Estado (Novo)
- Componente: `frontend/src/components/BrazilStatesMap.vue`.
  - Baseado no pacote `@svg-maps/brazil` para os caminhos SVG dos estados.
  - ViewBox dinâmico remove bordas vazias; altura configurável via prop `height` (0 = auto; padrão 560).
  - Labels das UFs centralizadas e em maiúsculas, com ajuste para estados pequenos.
  - Hover com destaque (borda azul e brilho leve).
  - Colorização opcional por gradiente baseada em `salesByUf` (apenas estados com venda recebem cor).
- Integração na tela `frontend/src/views/Dashboard.vue`:
  - O bloco “Configurações” foi substituído pela seção “Distribuição Geográfica”.
  - Ao clicar em um estado, o front chama `GET /api/core/dashboard/?state=UF`; só abre o modal após o carregamento.
  - `LoadingOverlay` cobre o card do mapa enquanto os dados do estado são carregados.

### Dashboard — Atualizações visuais e de fluxo (2025-09)
- Barra superior
  - Inclui botão “Verificar Carreira” (Licenciado) que chama o backend e abre modal de resultado.
  - Removido chip de “Contrato: Pendente/Assinar”; aviso movido para o acordeon de alertas.
- Cards
  - Card “Documentação” reintroduzido com layout cinza suave; exibe PF e PJ com bolinhas de status:
    - Verde: aprovado; Amarelo: pendente/incompleto; Azul: aguardando; Vermelho: não enviado/reprovado.
  - Ordem de cards do Licenciado: Rede, Usinas Vendidas, Projeção de Bônus, Carreira Atual (no header), Pontos Projetados, Pontos Consolidados, Saldo Disponível, Documentação.
- Alertas
  - Acordeon agrega: contrato pendente (CTA “Reenviar Contrato”), documentos PF/PJ pendentes (CTA “Enviar Documentos”/“Minhas Empresas”), pagamento anual pendente (CTA “Pagar Agora”).
  - Sininho no header global mostra contador de alertas e abre modal com mensagens importantes.

## Backend (Django + DRF)
### Finance (Saque — Novo)
- Models:
  - `finance.WithdrawRequest`: acrescido de estados/campos para aprovação, agendamento, emergência e cancelamento (`approved_by/at`, `scheduled_for/by`, `expected_payout_date`, `emergency_reason`, `canceled_by/at`, `cancel_reason`, status `scheduled`).
  - `finance.WithdrawRequestLog`: trilha de auditoria com ações (`requested`, `approved`, `scheduled`, `emergency_released`, `canceled`, `processed_paid`, `processed_rejected`, `processing`).
- Serializers/Views/URLs:
  - `api/finance/withdraw-requests/` (CRUD autenticado; licenciado vê/cria próprios; operador/superadmin filtram por `licensed_id`).
  - Ações:
    - `POST /api/finance/withdraw-requests/{id}/approve/` — define aprovação e previsão (somente operador/superadmin).
    - `POST /api/finance/withdraw-requests/{id}/schedule/` — agenda processamento (somente operador/superadmin).
    - `POST /api/finance/withdraw-requests/{id}/emergency_release/` — liberação emergencial (motivo obrigatório; processa imediato ignorando janela) (somente operador/superadmin).
    - `POST /api/finance/withdraw-requests/{id}/cancel/` — cancela pendente/agendado (operador/superadmin; licenciado pode cancelar o próprio).
    - `GET /api/finance/withdraw-requests/{id}/history/` — histórico completo da solicitação.
- Regras de validação:
  - Bloqueio de múltiplas pendentes por licenciado; valida mínimo e saldo; snapshot da conta na resposta; taxa fixa via `WITHDRAW_FEE_FIXED` e janela via `WITHDRAW_ALLOWED_*`.
- Processamento PIX (Sicoob):
  - Cliente `SicoobPixClient` realiza POST `{{base_url}}/pagamentos` (Pix Pagamentos v2). Não há suporte oficial mapeado para agendamento nativo de PIX; portanto, agendamento é feito no banco e processado por rotina.
  - Serviço `process_withdraw_request` debita saldo, cria `Transaction` e integra com Sicoob; atualiza `paid`/`rejected` e registra logs.
- Tarefa periódica:
  - `finance.tasks.process_scheduled_withdraws` — processa `scheduled` vencidos, ignorando janela, para execução diária (Celery Beat).

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
- Reenvio de Contrato
  - `POST /api/contracts/templates/resend-adesion/` — reenvia contrato de adesão via Lexo para o e‑mail do licenciado atual.
- Remoções
  - `ContractLog` removido do projeto (model/admin), migração criada e referências limpas em `contracts/services.py`.

### Network
- Admin: registrado `ScoreReference` (listagem, filtros, busca) em `network/admin.py`.
- Novo endpoint `api/network/upline-chain/` que retorna a cadeia de uplines (imediato até raiz) para um licenciado; utilizado no modal de Relatório do Licenciado.

### Core
- `LicensedCompany` (novo)
  - N:1 com `core.Licensed` (um licenciado pode ter várias empresas/CNPJs).
  - Campos principais: `cnpj`, `razao_social`, `nome_fantasia`, `insc_estadual`, `insc_municipal`, `cep`, `city_lookup`, `endereco`, `numero`, `complemento`, `bairro`, `telefone`, `observacao`, `stt_validate` (pending/rejected/approved), `rejection_reason`, timestamps.
- `LicensedDocument` — novos campos e unicidade PF/PJ.
- `Licensed` — `stt_document` para dashboard; sinais ajustados.
- Dashboard com filtro por UF: `GET /api/core/dashboard/?state=UF`.

## Rotas/Endpoints (resumo)
- Finance:
  - `api/finance/bank-accounts/`
  - `api/finance/withdraw-requests/`
  - `POST /api/finance/withdraw-requests/{id}/approve/`
  - `POST /api/finance/withdraw-requests/{id}/schedule/`
  - `POST /api/finance/withdraw-requests/{id}/emergency_release/`
  - `POST /api/finance/withdraw-requests/{id}/cancel/`
  - `GET  /api/finance/withdraw-requests/{id}/history/`
- PixConfig: `api/finance/pix-config/`
- Gateway (Pagar.me): `api/finance/gateway-config/`
- Transações/Saldo: `api/finance/transactions/`, `api/finance/virtual-account/balance/`
- Demais: plans, notifications, contracts, core, network (como já descrito acima).

## Migrações
- Finance: criação de `WithdrawRequestLog` e extensão de `WithdrawRequest` com campos de aprovação/agendamento/emergência/cancelamento.

## Pendências/Operação
- Executar migrações após alterações do backend:
  - `python manage.py migrate`
- Configurar Celery Beat para executar `finance.tasks.process_scheduled_withdraws` diariamente (ou conforme janela definida).
- Garantir token de sandbox para testes Sicoob (ou OAuth2 + mTLS em homolog/produção).

---
Atualizado por: Assistente (Aquiles) — data da última consolidação conforme execução das tarefas recentes.
