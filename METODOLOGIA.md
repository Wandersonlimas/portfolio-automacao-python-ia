# Metodologia, escopo e dicionário de dados

## 1. Natureza e população

Este é um **case com dados 100% sintéticos**, sem qualquer relação com empresas reais. Foram gerados 5.400 pedidos-base, distribuídos de 01/08/2026 a 31/10/2026. O gerador insere intencionalmente linhas duplicadas e inválidas. A semente pseudoaleatória é fixa: `20261108`.

A referência operacional de comparação é `2026-11-01T00:00:00`. Nenhuma métrica depende da data real da máquina do usuário.

## 2. Três fontes

**pedidos.csv:** `pedido_id` (chave), `criado_em` (ISO local, sem fuso), `canal` (`Marketplace A`, `Marketplace B`, `Site próprio`), `categoria`, `itens` e `valor_brl` (texto monetário com ponto decimal, sem separador de milhar).

**pagamentos.csv:** `pedido_id`, `status_pagamento` (`confirmado`, `pendente`, `recusado`), `valor_pago_brl` e `confirmado_em`.

**expedicoes.csv:** `pedido_id`, `expedido_em` e `transportadora` (operadores logísticos fictícios).

Todos os valores monetários são convertidos com `decimal.Decimal` para **centavos inteiros**, evitando erros de precisão com ponto flutuante.

## 3. Verificação de qualidade e quarentena

A ingestão recusa (com registro da linha e do motivo): ID ausente, ID duplicado, valor não positivo, quantidade inválida, canal inválido, data inválida ou fora de período, campo/tipo inválido. A primeira ocorrência válida de ID é considerada; a cópia posterior é rejeitada. O filtro de data é 01/08/2026 (inclusive) até 01/11/2026 (exclusive).

`linhas_rejeitadas.csv` documenta as exclusões. Os indicadores são calculados **somente após a quarentena**. O conjunto também registra duplicações detectadas nas fontes secundárias, quando existentes.

## 4. Conciliação e regras de exceção

Cada pedido válido é ligado ao primeiro pagamento e à primeira expedição com o mesmo `pedido_id`.

| Regra | Condição | Efeito |
|---|---|---|
| Pagamento ausente | Sem registro correspondente | Cria exceção; não entra em valor conciliado |
| Status inválido | Pagamento com status fora do conjunto | Cria exceção |
| Divergência de valor | Pagamento confirmado com diferença absoluta superior a **1 centavo** | Cria exceção; exclui do valor conciliado |
| Valor pago inválido | Texto monetário não interpretável | Cria exceção; exclui do valor conciliado |
| Sem expedição | Pagamento confirmado sem linha de expedição | Cria exceção separada |
| Expedição anterior | Data de envio anterior ao pedido | Cria exceção, desconsiderada no indicador SLA |
| SLA excedido | Pedido confirmado despachado após 48h da criação | Cria exceção |

### Definições matemáticas

`pedidos_validos = |{id validado}|`

`taxa_excecao = |{pedido válido com ao menos uma exceção}| / pedidos_validos × 100`

`SLA = |{confirmado e expedido com 0 ≤ horas ≤ 48}| / |{confirmado e expedido com horas ≥ 0}| × 100`

`valor_conciliado = Σ valor_pedido_centavos` onde status é `confirmado` e não há motivo `Divergência de valor` nem `Valor pago inválido`.

`taxa_validacao = linhas_validas / linhas_brutas × 100`

**Atenção:** pedidos confirmados sem expedição **não** entram no denominador do SLA de expedição. Existe um indicador de exceção específico para eles. O denominador não deve ser interpretado como SLA de todas as vendas.

## 5. Diagnóstico automatizado

O módulo `insights.py` extrai as três observações por regra: exceção mais frequente, cobertura do controle e SLA. Isso é **lógica determinística**, e não IA generativa. A integração `ia_opcional.py`, não executada por padrão, faz chamadas HTTP à Responses API somente quando há `OPENAI_API_KEY` e `OPENAI_MODEL`. Envia **somente KPIs/qualidade/séries sintéticos agregados**.

Os textos gerados por IA não são validados automaticamente contra cada número. Quem executar a integração deve revisar e aprovar o resultado manualmente antes de qualquer publicação. O sistema **não aceita narrativas geradas por IA como entrada para os cálculos**.

## 6. Limitações

A simulação é controlada: não tem custo do trabalho humano, apropriação de despesas, devoluções, conciliação bancária, imposto, cancelamentos após confirmação, feriados ou calendário de transportadora. Horários são locais sem timezone, definidos por convenção para o case. O valor conciliado não equivale a faturamento contábil, fluxo de caixa ou DRE.

Os erros e rupturas são programados e não demonstram a realidade de nenhum negócio. O exercício não mede ganhos reais de prazo, economia, precisão ou produtividade.
