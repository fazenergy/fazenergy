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
- Páginas alvo para aplicar o padrão: Rede (Diretos, Rede Completa, Árvore da Rede, Adesões) e todas as demais listagens do sistema.

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

### Gerenciar Usuários (Plano de Execução)
- Objetivo: criar visão administrativa completa (somente Superadmin) para manutenção de Usuários, Perfis/Permissões e Grupos, seguindo o padrão de barra de botões, filtros e grid.

- Escopo das Telas
  1) Usuários
     - Grid com colunas: ID, Username, Nome, E-mail, Ativo, Última atualização.
     - Filtros: Texto (username/nome/e-mail), Grupo, Status (ativo/inativo).
     - Ações: Adicionar, Exportar, Imprimir.
     - Modal de Cadastro/Edição com abas:
       - Dados (username, e-mail, senha/confirmar, nome, ativo, imagem de perfil).
       - Grupos & Permissões (seleção de grupos existentes; permissões granulares opcionais).
       - Layout do topo à esquerda com anexo de foto, igual ao cadastro de Licenciado.
  2) Perfis (Permissões)
     - Grid de permissões do Django (app_label, codename, name).
     - Filtros por app e busca.
     - Ações: Exportar, Imprimir.
  3) Grupos
     - Grid com colunas: ID, Nome do Grupo, Qtde de Permissões.
     - Filtros por texto.
     - Ações: Adicionar, Exportar, Imprimir.
     - Modal para criar/editar e vincular permissões ao grupo.

- Backend (APIs)
  - Endpoints autenticados (somente superadmin):
    - `api/admin/users/` (CRUD de usuários)
    - `api/admin/groups/` (CRUD de grupos + vincular permissões)
    - `api/admin/permissions/` (listagem)
  - Regras:
    - Senhas só são obrigatórias na criação; na edição, alterar apenas se os campos forem enviados.
    - Proteção para não remover o próprio superadmin único do sistema.

- Frontend (Vue)
  - Rotas protegidas (meta: requiresAuth + role superadmin):
    - `/admin/users`, `/admin/groups`, `/admin/permissions`.
  - Telas com DataTable padrão, filtros e barra de botões (Adicionar/Exportar/Imprimir).
  - Modais com o mesmo padrão visual e validações de campos obrigatórios.

- Entregáveis (ordem)
  1) Implementar APIs (users, groups, permissions) no backend.
  2) Telas de Grupos e Permissões (mais simples) no frontend.
  3) Tela de Usuários com modal em abas (Dados; Grupos & Permissões).
  4) Integração de exportar/imprimir e validações finais.

### Dependências e Notas
- Sem novas dependências obrigatórias neste escopo (reuso das bibliotecas atuais: DRF, DataTable, etc.).

Atualizações aplicadas (2025-08)
- Header (global)
  - Breadcrumbs dinâmicos ativados para: Rede (Diretos, Rede Completa, Adesões, Árvore da Rede), Licenciados, Documentos e Relatórios (Pontos, Bônus).
  - Remover breadcrumbs locais das páginas que ainda tiverem duplicidade.
- Dashboard
  - Barra superior com botões: Convidar Licenciado (verde), Exportar (roxo), Imprimir (azul). Para superadmin, manter também Cadastrar Licenciado (verde).
  - Exportar/Imprimir exportam as métricas atuais (cards) em XLS e impressão simples.
  - Bloco “Distribuição Geográfica”: mapa do Brasil clicável por UF com abertura de modal de totais filtrados por estado. Ao clicar, os dados são pré-carregados e o modal só é aberto após o retorno da API; um overlay de loading cobre o card do mapa durante a requisição.
  - Conteúdo do modal com margem superior de 10px e espaçamento de 20px antes do rodapé.
  - Regras de contagem no Dashboard:
    - Total de Licenciados: considera somente licenciados que possuam ao menos uma adesão confirmada (paga).
    - Resumo Operacional — Pré‑Cadastros (30 dias): licenciados criados nos últimos 30 dias que possuem apenas adesões não pagas (pending/canceled) e nenhuma adesão confirmada.
    - Resumo Operacional — Ativações: licenciados com adesão confirmada com data de pagamento há 20 dias ou mais (liberação após 20 dias).

- Rede
  - Diretos, Rede Completa, Adesões: toolbar padronizada (botões + filtros + busca expansível) sem borda, com footer do grid colado ao rodapé do container.
  - Árvore da Rede: endpoint ajustado para retornar URL ABSOLUTA da imagem de perfil (garante render no front).
- Licenciados
  - Lista padronizada com toolbar (Adicionar, Exportar, Imprimir) e busca expansível.
- Relatórios
  - Pontos e Bônus: toolbar padronizada com Exportar/Imprimir, filtros e busca expansível; breadcrumbs no header.
  - Fechamentos: botão Info com regras e modal “Solicitar Saque” (licenciado); ao selecionar a conta, preenche automaticamente banco/tipo/agência/conta (campos bloqueados) e permite informar o valor.
- Documentos do Licenciado
  - Padronizar a tela com a mesma toolbar (Exportar/Imprimir, filtro de status, busca expansível) e grid com footer fixo.
  - Ações “Anexar/Reenviar” em modal com botões “Fechar/Gravar”.
- UX/Estilo global
  - Botões primários de “Gravar/Salvar”: cor verde (bg-emerald-600, hover:bg-emerald-700).
  - Inputs `readonly` devem exibir fundo cinza claro e sem foco (aplicado no componente `Input.vue`).

### Documentos do Licenciado (Novo)
- Rotas:
  - `/documents` (licenciado) — anexar/reenviar CPF, RG, Comprovante de Endereço, PIS; grid + modal padrão.
  - `/documents/review` (operador/superadmin) — revisar/aprovar/reprovar documentos pendentes.
- Dashboard:
  - Card “Documentação do Licenciado” com gradiente amarelo/laranja.
  - Alertas no topo quando pendente e quick action “Enviar Documentos”.
- UX:
  - Botões: “Anexar” no grid; modal com “Fechar/Gravar”.
  - Erros de anexos exibidos dentro do modal (sem alert).

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
### Plans
- `PlanCareer` API
  - Serializer `PlanCareerSerializer`.
  - ViewSet `PlanCareerViewSet`.
  - Rota: `api/plans/plan-careers/` (CRUD autenticado).
- `PlanAdesionSerializer`: incluído `licensed_username` para exibir `id-username` no front.

- Verificação/Evolução de Carreira
  - Endpoint `POST /api/core/career/verify/`:
    - Calcula pontos válidos (`ScoreReference.status='valid'`), diretos e vendas de usina aprovadas.
    - Seleciona o maior `PlanCareer` que atende `required_points`, `required_directs` e `required_direct_sales` e atualiza `Licensed.current_career`.
    - Resposta inclui `updated`, `before`, `after`, `metrics {points,directs,sales}`, `next {stage_name,required_*}` e `missing {points,directs,sales}`.

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

### Finance (Saque — Novo)
- Models:
  - `finance.BankAccount`: contas bancárias do licenciado (PF/PJ com vínculo opcional a `core.LicensedCompany` aprovada).
  - `finance.WithdrawRequest`: solicitações de saque com status (`pending|processing|paid|canceled|rejected`), taxas e impostos.
- Serializers/Views/URLs:
  - `api/finance/bank-accounts/` (CRUD autenticado; retorna/edita apenas contas do usuário corrente; operador/superadmin podem filtrar por `licensed_id`).
  - `api/finance/withdraw-requests/` (CRUD autenticado; criação valida saldo, mínimo, bloqueia duplicadas pendentes e retorna snapshot do banco).
- Regras de validação:
  - Conta PJ exige empresa aprovada; PF não permite empresa.
  - Solicitação bloqueada se já existir `pending` para o licenciado.
  - Valor mínimo e taxa fixa via `WITHDRAW_MIN_VALUE` e `WITHDRAW_FEE_FIXED`.

### Contracts (Lexo)
- APIs
  - `api/contracts/config/` (singleton GET/POST/PUT de `ContractConfig`).
  - `api/contracts/templates/` (CRUD de `ContractTemplate`).
- Reenvio de Contrato
  - `POST /api/contracts/templates/resend-adesion/` — reenvia contrato de adesão via Lexo para o e‑mail do licenciado atual.
  - Front exibe modal de confirmação: “Contrato reenviado para o e‑mail {email}”.
- Remoções
  - `ContractLog` removido do projeto (model/admin), migração criada e referências limpas em `contracts/services.py`.

### Network
- Admin: registrado `ScoreReference` (listagem, filtros, busca) em `network/admin.py`.
- Novo endpoint `api/network/upline-chain/` que retorna a cadeia de uplines (imediato até raiz) para um licenciado; utilizado no modal de Relatório do Licenciado.

### Core
- `LicensedCompany` (novo)
  - N:1 com `core.Licensed` (um licenciado pode ter várias empresas/CNPJs).
  - Campos principais: `cnpj` (único), `razao_social`, `nome_fantasia`, `insc_estadual`, `insc_municipal`, `cep`, `city_lookup`, `endereco`, `numero`, `complemento`, `bairro`, `telefone`, `observacao`, `stt_validate` (pending/rejected/approved), `rejection_reason`, timestamps.
- `LicensedDocument`
  - Acrescentado `owner_type` (`pf`|`pj`) e FK opcional `company` (quando `owner_type='pj'`).
  - Unicidade:
    - PF: (`licensed`, `owner_type`, `document_type`).
    - PJ: (`company`, `document_type`).
  - Novos tipos: `cnpj_card` (Cartão CNPJ) e `social_contract` (Contrato Social).
- `Licensed`
  - Campo `stt_document` (pending/rejected/approved) usado pelo Dashboard.
  - Regras de sinal: recalcula automaticamente o `stt_document` quando documentos são criados/atualizados/excluídos.
- API
  - `api/core/licensed-documents/` (CRUD autenticado)
    - Licenciado cria/edita apenas os próprios; operador vê todos e pode aprovar/reprovar.
    - Upload via multipart; `licensed` inferido do usuário (operador deve informar explicitamente).
  - Dashboard expõe `documents.status` e `documents.pending`.
- Dashboard — Documentação PF/PJ
  - Card `docs_status` passa a trazer objeto `{ pf, pj }` com status independentes.
  - Estrutura `documents` inclui `pf`, `pj` e `company_cnpjs` para montar alertas direcionados (PF e PJ).
- `LicensedListSerializer` expandido para suportar `documents_status` derivado (pendente, incompleto, aguardando aprovação, aprovado) e cidade/UF com ids.
- `LicensedViewSet` ganhou action para operadores/superadmins atualizarem campos do usuário vinculado (nome, e‑mail, senha, foto) de forma segura.
- Notificações
  - Envio de e-mail para operadores quando o conjunto obrigatório estiver completo e pendente de validação (template: `LicensedDocsSubmitted`).
  - Removidos campos `previous_career` e `dtt_previous_career`.
  - Ajustes no método de qualificação para carreira atual.
  - Admin `LicensedAdmin` atualizado (sem carreira anterior, `fieldsets` e validações ajustados).
- Endpoint do Dashboard com filtro por UF (novo)
  - `GET /api/core/dashboard/?state=UF` (admin/operador)
    - Filtra por `Licensed.city_lookup__state__uf` quando aplicável.
    - Adesões pagas: filtra por UF do licenciado da adesão (join até `Licensed`).
    - Bônus: filtra por UF via `Transaction.virtual_account.licensed.city_lookup.state.uf`.
    - Pontos: filtra por UF via `ScoreReference.receiver_licensed.city_lookup.state.uf`.
    - Resumo (pré-cadastros, ativações, solicitações de saque) respeita a UF.

#### Segurança do Login (atual)
- Endpoint `POST /api/token/` usa `SecureTokenObtainPairView` com bloqueio temporário após 5 tentativas falhas por usuário (lockout por cache).
- Throttling e 2FA foram desativados neste momento conforme decisão de produto.
- Parâmetros ajustáveis (em `settings.py`):
  - `LOGIN_LOCKOUT_FAILURES` (padrão 5)
  - `LOGIN_LOCKOUT_WINDOW` (padrão 900s)
  - `LOGIN_LOCKOUT_DURATION` (padrão 900s)

## Rotas/Endpoints (resumo)
- Plans: `api/plans/plan-careers/`
- Notifications: `api/notifications/config/`, `api/notifications/templates/`, `api/notifications/templates/{id}/test/`
- Finance: `api/finance/gateway-config/`, `api/finance/transactions/?licensed_username=&month=&year=`, `api/finance/virtual-account/balance/`
 - Finance: `api/finance/gateway-config/`, `api/finance/transactions/?licensed_username=&month=&year=`, `api/finance/virtual-account/balance/`, `api/finance/bank-accounts/`, `api/finance/withdraw-requests/`
- Contracts: `api/contracts/config/`, `api/contracts/templates/`
- Core: `api/core/licensed-documents/`, `api/core/licensed-documents/pending/`, `api/core/licensed-companies/`, `api/core/dashboard/?state=UF`
- Network: `api/network/upline-chain/`, `api/network/tree/`

## Frontend — Atualizações relevantes
- Licenciados
  - Toolbar padrão (Adicionar, Exportar, Imprimir) e busca expansível.
  - Ações por linha: Editar (azul), Relatórios (cinza), Extrato Virtual (roxo), Trocar Senha (laranja). Botão de Upline removido.
  - Modal de Relatório: mantém informações do licenciado e acrescenta grid “Upline | Nível”.
  - Modal Extrato Virtual: filtros Mês/Ano, saldo disponível no topo e grid (ID, Data Cadastro, Referência — origem Adesão/Usina, Descrição, Valor, Operação, Status).
  - CEP com preenchimento automático (ViaCEP) e máscaras de Telefone/CEP/CPF.
  - Modal Edição: `username` somente leitura; campos de senha removidos.
  - Modal Trocar Senha: campos sempre limpos ao abrir; validação forte e alert flutuante com [×].


## Migrações
- Contracts: deleção de `ContractLog`.
- Core: criação de `LicensedDocument`; inclusão de `Licensed.stt_document`.
- Plans/Notifications/Finance/Contracts: novas rotas/serializers/views sem alterações de esquema além das citadas.

## Pendências/Operação
- Executar migrações após alterações do backend:
  - `python manage.py migrate`
- Garantir token JWT válido para acessar rotas autenticadas no front.
- Opcional: integrar CKEditor 5/Monaco oficiais se necessário (dependências de build).

### Dependências adicionadas (Frontend)
- `@svg-maps/brazil` — shapes SVG dos estados do Brasil para o componente de mapa.
  - Instalação (no diretório `frontend/`):
    - `npm install @svg-maps/brazil`
  - Reinicie o Vite após instalar.

Observação: avaliamos `vue3-svg-map`, mas a solução final não depende dela; usamos apenas `@svg-maps/brazil` e renderização SVG nativa.

---
Atualizado por: Assistente (Aquiles) — data da última consolidação conforme execução das tarefas recentes.
