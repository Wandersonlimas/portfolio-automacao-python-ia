# Case 02 | Automação e Controle de Operações Multicanal

**Portfólio técnico de Wanderson Limas**  
**Python · ETL · Integração de fontes · Qualidade de dados · Business Intelligence · HTML/CSS/JavaScript · Integração opcional com IA**

[**▶ Explorar dashboard interativo**](https://wandersonlimas.github.io/portfolio-automacao-python-ia/) · [**Ver código e documentação**](https://github.com/Wandersonlimas/portfolio-automacao-python-ia) · [**Ler relatório executivo (PDF)**](entregaveis/Relatorio_Executivo_Automacao_Python_IA.pdf)

![Prévia do dashboard de Automação e Controle](entregaveis/Preview_Case2_V2.png)

> **Estudo demonstrativo, 100% sintético.** Todos os valores, IDs e situações foram simulados por software. Este material não demonstra resultados de um empregador, clientes reais nem ganhos efetivamente obtidos. Desenvolvido com assistência de IA e acompanhado de código reproduzível, documentação e testes.

## Desafio simulado

Integrar dados de pedidos, pagamentos e expedições de uma operação multicanal, automatizando validações, conciliação financeira por ID, monitoramento do SLA de despacho e geração de relatórios gerenciais.

## Dashboard V2

Acesse o [dashboard publicado no GitHub Pages](https://wandersonlimas.github.io/portfolio-automacao-python-ia/). A versão de distribuição, `index.html`, é autocontida, sem backend ou bibliotecas externas, e também pode ser aberta localmente.

- **Gerencial:** cinco indicadores auditáveis, evolução mensal, distribuição por canal, motivos de exceção, conciliação e diagnósticos por regra.
- **Operacional:** incidência por canal, fila de prioridades, pesquisa, ordenação, paginação, detalhamento e exportação CSV de todo o recorte.
- **Engenharia:** arquitetura, qualidade de ingestão, artefatos, definições matemáticas e limitações.
- **Filtros compartilhados:** mês, canal, categoria, status de pagamento e tipo de ocorrência.

## Estrutura de pastas

Os módulos de interface foram separados em `src/web/templates/`, `src/web/css/` e `src/web/js/`. A geração do arquivo HTML final é feita por `codigo/gerar_dashboard.py`. Consulte o mapa completo em [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

## Reproduzir a geração

Requer Python 3.10+ e as dependências de `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python codigo/executar.py
python -m unittest discover -s testes -v
```

No Windows, ative `.venv\\Scripts\\activate` e use `python` quando não houver `python3`.

## Fontes e saídas

| Artefato | Local | Finalidade |
|---|---|---|
| Dados de entrada | `dados/brutos/*.csv` | Três fontes fictícias, com problemas deliberados |
| Processamento | `codigo/pipeline.py` | Validação, reconciliação e métricas determinísticas |
| Auditoria | `dados/processados/*` | Linhas rejeitadas, exceções e resultados por pedido |
| Código frontend | `src/web/` | Interface com módulos separados |
| Dashboard pronto | `index.html` | Site estático para publicação em GitHub Pages |
| PDF executivo | `entregaveis/Relatorio_Executivo_Automacao_Python_IA.pdf` | Relatório de dados e metodologia |
| Miniatura | `entregaveis/Miniatura_LinkedIn_Automacao_Case2.png` | Capa para divulgação do estudo |
| Testes | `testes/` | Regras, fórmulas e consistência dos artefatos |

## Principais definições

**Taxa de exceção** = pedidos válidos com ≥1 ocorrência / pedidos válidos.  
**SLA** = pedidos confirmados despachados em ≤48h / pedidos confirmados despachados com tempo válido.  
**Conciliação** = confirmados com divergência de, no máximo, R$ 0,01, seguindo a regra do ETL.  
**Receita conciliada** = soma de pedidos confirmados sem divergência. Não representa receita contábil ou margem.

**Qualidade global** = linhas válidas / linhas brutas do arquivo de pedidos, sem aplicação dos filtros da interface.

## IA: delimitação técnica

O dashboard apresenta **análises determinísticas**, executadas no navegador. O módulo `codigo/ia_opcional.py` demonstra como integrar um LLM por API mediante configuração explícita e credenciais próprias; **não foi executado como parte das análises publicadas**.

Não envie dados confidenciais para APIs externas. O material fornecido não exige chave de API e não contém dados corporativos reais.

## Publicação e apresentação profissional

**Status:** repositório público e dashboard publicado pelo GitHub Pages, na branch `main` e pasta raiz `/`.

- **Aplicação ao vivo:** https://wandersonlimas.github.io/portfolio-automacao-python-ia/
- **Código-fonte:** https://github.com/Wandersonlimas/portfolio-automacao-python-ia
- **Orientações para inclusão no LinkedIn:** [docs/PUBLICACAO_GITHUB_LINKEDIN.md](docs/PUBLICACAO_GITHUB_LINKEDIN.md)
- **Arquitetura e decisões técnicas:** [docs/ARQUITETURA.md](docs/ARQUITETURA.md)
- **Metodologia e limitações:** [METODOLOGIA.md](METODOLOGIA.md) e [docs/EVOLUCAO_V2.md](docs/EVOLUCAO_V2.md)

Este é um projeto demonstrativo, não uma implantação empresarial. Os indicadores são simulados e não devem ser apresentados como ganhos comprovados de produtividade, receita ou economia.
