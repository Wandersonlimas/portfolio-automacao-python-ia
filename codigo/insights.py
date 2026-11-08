"""Diagnóstico determinístico: não é saída de IA generativa."""
from collections import Counter


def gerar_insights(kpis: dict, serie: list[dict]) -> list[dict]:
    motivos = Counter(kpis['motivos_excecao'])
    destaques = motivos.most_common(3)
    insights=[]
    if destaques:
        tipo,n=destaques[0]
        insights.append({'titulo':'Principal frente de investigação',
                         'texto':f'{tipo}: {n:,} ocorrências sinalizadas. Priorizar a validação da regra e da causa raiz antes de propor ações.',
                         'nivel':'Atenção'})
    insights.append({'titulo':'Cobertura do controle',
                     'texto':f"{kpis['pedidos_com_excecao']:,} pedidos com ao menos uma exceção entre {kpis['pedidos_validos']:,} linhas válidas ({kpis['taxa_excecao_pct']:.1f}%).",
                     'nivel':'Controle'})
    insights.append({'titulo':'SLA de expedição',
                     'texto':f"{kpis['expedidos_no_prazo']:,} de {kpis['despachados']:,} pedidos expedidos tiveram despacho em até 48 horas ({kpis['sla_pct']:.1f}%). Não inclui pedidos sem expedição no denominador.",
                     'nivel':'Indicador'})
    return insights
