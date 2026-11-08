# Evolução visual e funcional · V2.0

## Motivação

Evoluir o primeiro dashboard do Case 02 para uma aplicação analítica de maior densidade de informação, melhor hierarquia visual e componentes adequados à gestão e investigação operacional.

## Alterações implementadas

1. Barra superior compacta, identidade própria azul-marinho e verde-petróleo, sem marca de terceiros.
2. Visões independentes: **Gerencial**, **Operacional** e **Engenharia**.
3. Cinco filtros globais sincronizados: mês, canal, categoria, status de pagamento e tipo de ocorrência.
4. Painel gerencial com KPIs, tabela mensal, distribuição por canal, causas de exceções e conciliação.
5. Painel operacional com busca, ordenação, navegação paginada e detalhe de cada registro.
6. Exportação CSV de todos os registros do recorte e da pesquisa operacional, não apenas os registros visíveis na página atual.
7. Área de auditoria com qualidade global do ETL, estágios do pipeline, fórmulas e limites.
8. Frontend modular em `src/web/` e HTML compilado para a raiz, sem dependências de rede.
9. Testes de integridade e compilação.

## Referências

Os projetos do portfólio privado do autor foram usados somente como **referência de princípios de UX e organização**. Nenhum arquivo do Drive, código de integração corporativa, base operacional real ou identidade visual de empresa foi copiado para a versão pública.

## Notas metodológicas

- A taxa de exceção conta **pedidos únicos** com ≥1 motivo.
- A tabela de motivos conta **ocorrências**; um pedido pode ter motivos múltiplos.
- SLA considera apenas pedidos **confirmados e expedidos** com tempo válido.
- A conciliação é feita somente para pagamentos **confirmados** com diferença de até 1 centavo frente ao pedido.
- O número de linhas rejeitadas é exibido como **global**, não como métrica filtrável.
- Diferença mensal em volume não é julgada como ganho/perda automaticamente; apenas variação descritiva.

## Pendências antes da publicação final

- Revisão humana dos critérios e cenários de negócio.
- Confirmar que os arquivos do relatório, miniatura e dashboard refletem a mesma versão.
- Publicar em repositório **independente**, sem modificar o Case 01 do LinkedIn.
