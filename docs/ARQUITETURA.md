# Arquitetura do Case 02 · Versão 2.0

O projeto é demonstrativo e funciona sem banco remoto, sem API corporativa e sem dados pessoais. A arquitetura toma como **referência de engenharia e UX** padrões dos projetos técnicos do autor: separação dos módulos, visão gerencial/operacional, filtros cruzados, exportações e validação rastreável. **Nenhum dado, marca ou trecho de código proprietário de terceiros foi incorporado.**

```text
Case2_Automacao_Python_IA_V2/
├── dados/
│   ├── brutos/                  # fontes geradas sinteticamente
│   │   ├── pedidos.csv
│   │   ├── pagamentos.csv
│   │   └── expedicoes.csv
│   └── processados/             # trilha de auditoria e dados consolidados
│       ├── pedidos_processados.csv
│       ├── linhas_rejeitadas.csv
│       ├── excecoes.csv
│       └── indicadores.json
├── codigo/                      # processamento de dados e montagem de entregáveis
│   ├── gerar_dados.py
│   ├── pipeline.py
│   ├── insights.py
│   ├── gerar_dashboard.py
│   ├── gerar_relatorio.py
│   ├── ia_opcional.py
│   └── executar.py
├── src/web/                     # frontend modular e editável
│   ├── css/dashboard.css
│   ├── js/dashboard.js
│   └── templates/dashboard.html
├── entregaveis/
│   ├── dashboard_offline.html   # cópia auto-contida do index
│   ├── Preview_Case2_V2.png
│   ├── Miniatura_LinkedIn_Automacao_Case2.png
│   └── Relatorio_Executivo_Automacao_Python_IA.pdf
├── testes/
│   ├── test_pipeline.py
│   └── test_dashboard.py
├── docs/
│   ├── ARQUITETURA.md
│   ├── PUBLICACAO_GITHUB_LINKEDIN.md
│   └── EVOLUCAO_V2.md
├── METODOLOGIA.md
├── requirements.txt
├── README.md
└── index.html                  # publicação pronta para GitHub Pages
```

## Fluxo de execução

`gerar_dados → processar → gerar_dashboard + gerar_relatorio`.

O código-fonte HTML/CSS/JS é modular, mas `gerar_dashboard.py` incorpora CSS, JS e um subconjunto compacto dos registros processados em um único `index.html`. Assim, o arquivo público é autocontido, sem dependências de CDN, funcionando diretamente no navegador.

## Interface

**Gerencial:** cinco KPIs calculados sobre o recorte atual, séries mensais, composição por canal, principais exceções, conciliação e leitura determinística do cenário.

**Operacional:** visão de exceções por canal, prioridades, base analítica com IDs completos, pesquisa, ordenação, paginação, inspeção por registro e CSV da seleção em tela.

**Engenharia:** fluxo em cinco etapas, qualidade de ingestão (global), inventário de artefatos, fórmulas e limites. A qualidade global não muda com filtros, por não ter granularidade de linhas rejeitadas nas dimensões da operação.

## Proteção e transparência

- Todos os IDs, dados e valores são gerados por software com `seed=20261108`.
- O site não executa IA generativa, não exige credenciais nem envia dados a serviços externos.
- A análise por regras é descrita como determinística; o conector IA é uma integração desligada por padrão.
- Não incluir nesta pasta arquivos corporativos, screenshots identificáveis, nomes de clientes, logomarcas ou dados do usuário.
- O dashboard pode ser publicado sem nenhum serviço externo.
