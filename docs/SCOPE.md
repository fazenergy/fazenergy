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
- `tb_Plan` — cadastro de planos MMN (pontos, bônus por nível)
- `tb_PlanAdesion` — controle por afiliado (status/contrato/flags)
- `tb_Afiliate` — base de afiliados
- `tb_ContaVirtual`, `tb_Transacoes`, `tb_Recebimento` — gestão financeira
- Estruturas de rede com compressão e níveis
- Pipeline de lead→financiamento→instalação (status via API + Webhook REVO)

## Responsabilidades (DEV)
- Aquiles: rede, usuários, adesão, contratos, notificações, contas virtuais, compressão
  - Pendências: Pagar.me (saque), automação de qualificação, log de falhas
- Rodrigo: integrações com REVO (simulações, CEP, envio de docs, Webhook)

## Pontos Críticos de Negócio
- Sustentabilidade: receitas da REVO/oper. precisam cobrir instalação, bônus (incl. recorrentes) e custos
- Robustez do sistema (rede/financeiro/bônus) é essencial; transparência/estabilidade = diferencial

## Mudanças recentes (técnico)
- `core.Licensed`: removidos `city_name`/`state_abbr`; manter apenas `city_lookup`. Adicionado `dtt_activation` (DateTimeField).
- `core.Operator`: removidos `city_name`/`state_abbr`; manter apenas `city_lookup`.
- `network.Product`: novo model (`name`, timestamps) para catalogar produtos (ex.: usina, licença).
- `prospect` (novo app): `Prospect` (FK `network.Product`, FK `core.Licensed`), `Proposal` (FK `Prospect`), `ProposalResult` (FK `Proposal`). Rotas: `api/prospect/...`.
  - Observação: tabelas criadas com nomes iniciando em maiúsculas exigem aspas em SQL/IDE ("Prospect", "ProspectProposal", "ProspectProposalResult").

## Pendências técnicas alinhadas ao DER
- `plans.PlanAdesion.licensed` deve referenciar `core.Licensed` (hoje aponta para `User`).
- Ajustar `finance.PaymentLink.approve_payment` para usar `ind_payment_status`, `typ_payment`, `dtt_payment` em `PlanAdesion`.
- Corrigir `core.signals` para usar `network.UnilevelNetwork` com campos `upline_licensed/downline_licensed` (em vez de parent_licensed/child_licensed).

## Referências
- `docs/Faz Energy - Apresentação Institucional 2025.pptx`
- Notion: lucro e usina gratuita (links no arquivo `docs/Escopo`)
