# SCOPE — FazEnergyFinal

## Visão Geral
- Plataforma de afiliados no modelo MMN unilevel (5 níveis) para:
  - Adesão anual de afiliados (ativa posição na rede)
  - Venda de usinas fotovoltaicas com financiamento via REVO
  - Gestão de rede: bônus, pontos, plano de carreira, compressão dinâmica e recorrência

## Monetização
- Adesão anual: parte do valor remunera bônus; restante é receita
- Usinas FV: REVO financia/logística, Faz Energy instala/opera; economia do cliente gera fluxo recorrente que sustenta comissões

## Rede (MMN)
- Estrutura: unilevel 5 níveis; cada novo afiliado gera 300 pontos
- Liberação de bônus: após 20 dias do pagamento via cartão (segurança)
- Exibição separada: projeções x saldo disponível
- Compressão dinâmica: realoca bônus quando há inativos (puxa para próximo qualificado)

## Recorrência
- Em definição (com Raphael): pagamentos mensais por período (ex.: 24 meses)
- Avaliar se comissionamento é fixo ou variável conforme performance da usina/retornos da REVO

## Módulos Principais
- Gestão de afiliados: cadastro, adesão, ativação, renovação
- Gestão da rede: árvore unilevel, compressão
- Gestão financeira: carteira virtual, transações, recebimentos, Pagar.me (split/saque)
- Plano de carreira: qualificação por pontos, rotinas/automação
- Vendas de usinas: leads, simulação REVO, envio de documentos, contrato digital (Lexo Legal), status via Webhook
- Infraestrutura: EC2 (front/back/DB), S3 para arquivos, integrações (REVO, Lexo, Pagar.me)

## Entidades/Tabelas citadas (alto nível)
- `Plan` — cadastro de planos MMN (pontos, bônus por nível, template de contrato)
- `PlanAdesion` — transação de adesão (agora com FK `network.Product`)
- `Prospect` — lead/prospect (FK `core.Licensed`)
- `ProspectProposal` — proposta (FK `Prospect` e FK `network.Product`)
- `ProspectProposalResult` — resultado da proposta (FK `ProspectProposal`)
- `Product` — catálogo de produtos (ex.: “Usina”, “Licença/Adesão”)
- `ScoreReference` — referência de pontuação (origem genérica: `ProspectProposal` ou `PlanAdesion`)

## Rotas Ativas
- Backend: `api/core/`, `api/plans/`, `api/location/`, `api/network/`, `api/prospect/`

## Mudanças recentes (técnico)
- `prospect.Prospect`: removido relacionamento com `Product`.
- `prospect.Proposal`: adicionada FK `network.Product` (temporariamente nullable para migração rápida; objetivo: obrigatória).
- `plans.PlanAdesion`: adicionada FK `network.Product` (temporariamente nullable para migração rápida; objetivo: obrigatória).
- `network.ScoreReference`: criado com GenericForeignKey para origem (`ProspectProposal` ou `PlanAdesion`) e FKs para `core.Licensed`.
- App `proposal` (legado) removido do projeto.
- Observação: tabelas do app `prospect` usam nomes com maiúsculas e exigem aspas em SQL/IDE ("Prospect", "ProspectProposal", "ProspectProposalResult").

## Pendências técnicas alinhadas ao DER
- `plans.PlanAdesion.licensed` deve referenciar `core.Licensed` (hoje aponta para `User`).
- Ajustar `finance.PaymentLink.approve_payment` para usar `ind_payment_status`, `typ_payment`, `dtt_payment` em `PlanAdesion`.
- Corrigir `core.signals` para usar `network.UnilevelNetwork` com campos `upline_licensed/downline_licensed` (em vez de parent_licensed/child_licensed).
- Tornar `product` obrigatório (null=False) em `Proposal` e `PlanAdesion` após backfill.

## Referências
- `docs/Faz Energy - Apresentação Institucional 2025.pptx`
- Notion: lucro e usina gratuita (links no arquivo `docs/Escopo`)
