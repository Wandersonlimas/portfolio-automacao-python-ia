"""Pipeline ETL auditável. Apenas biblioteca padrão do Python.
Regras: duplicidade, dados inválidos, conciliação de pagamentos e SLA de expedição.
"""
from __future__ import annotations
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

CANAIS = {'Marketplace A', 'Marketplace B', 'Site próprio'}
STATUS = {'confirmado', 'pendente', 'recusado'}
SLA_HORAS = 48
REFERENCIA = datetime(2026, 11, 1, 0, 0)
CENTAVOS = Decimal('0.01')


def ler(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f, delimiter=';'))


def salvar_csv(path: Path, dados: list[dict], colunas: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=colunas, delimiter=';', extrasaction='ignore')
        writer.writeheader(); writer.writerows(dados)


def centavos(texto: str) -> int:
    try:
        dec = Decimal(texto).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
        if not dec.is_finite(): raise ValueError('valor não finito')
        return int(dec * 100)
    except (InvalidOperation, ValueError, TypeError) as e:
        raise ValueError('valor monetário inválido') from e


def data_iso(value: str) -> datetime:
    try: return datetime.fromisoformat(value)
    except (ValueError, TypeError) as e: raise ValueError('data inválida') from e


def limpar_pedidos(rows: list[dict]):
    corretos, rejeitados, vistos = [], [], set()
    for idx, r in enumerate(rows, 1):
        codigo = r.get('pedido_id','').strip()
        erro = None
        if not codigo: erro='ID ausente'
        elif codigo in vistos: erro='ID duplicado'
        else:
            vistos.add(codigo)
            try:
                total=centavos(r['valor_brl'])
                criado=data_iso(r['criado_em'])
                itens=int(r['itens'])
                if total <= 0: erro='Valor não positivo'
                elif itens < 1: erro='Quantidade inválida'
                elif r['canal'] not in CANAIS: erro='Canal inválido'
                elif not datetime(2026,8,1) <= criado < REFERENCIA: erro='Data fora do período'
            except (ValueError, KeyError, TypeError): erro='Campo ou tipo inválido'
        if erro: rejeitados.append({'linha':idx,'pedido_id':codigo,'motivo':erro})
        else: corretos.append({**r, '_centavos':total, '_criado':criado, '_itens':itens})
    return corretos, rejeitados


def processar(dados_brutos: Path, saida: Path) -> dict:
    dados_brutos,saida=Path(dados_brutos),Path(saida)
    pedidos_orig=ler(dados_brutos/'pedidos.csv')
    pedidos,rejeitados=limpar_pedidos(pedidos_orig)
    pagamentos_raw=ler(dados_brutos/'pagamentos.csv')
    expedicoes_raw=ler(dados_brutos/'expedicoes.csv')
    pagamentos={}; exp={}; infra=Counter()
    for r in pagamentos_raw:
        i=r.get('pedido_id','')
        if i in pagamentos: infra['Pagamento duplicado']+=1
        else: pagamentos[i]=r
    for r in expedicoes_raw:
        i=r.get('pedido_id','')
        if i in exp: infra['Expedição duplicada']+=1
        else: exp[i]=r
    registros=[]; excecoes=[]
    for p in pedidos:
        codigo=p['pedido_id']; pagamento=pagamentos.get(codigo); envio=exp.get(codigo)
        problemas=[]; pago=0; status='ausente'; enviado_em=''; horas=None
        if not pagamento: problemas.append('Pagamento ausente')
        else:
            status=pagamento.get('status_pagamento','')
            if status not in STATUS: problemas.append('Status de pagamento inválido')
            if status=='confirmado':
                try:
                    pago=centavos(pagamento['valor_pago_brl'])
                    if abs(pago-p['_centavos'])>1: problemas.append('Divergência de valor')
                except ValueError: problemas.append('Valor pago inválido')
        if status=='confirmado':
            if envio:
                try:
                    ts=data_iso(envio['expedido_em']); enviado_em=ts.isoformat(timespec='minutes')
                    horas=round((ts-p['_criado']).total_seconds()/3600,2)
                    if horas < 0: problemas.append('Expedição anterior ao pedido')
                    elif horas > SLA_HORAS: problemas.append('SLA de expedição excedido')
                except ValueError: problemas.append('Data de expedição inválida')
            else:
                problemas.append('Sem expedição até referência')
        registro={'pedido_id':codigo,'criado_em':p['_criado'].isoformat(timespec='minutes'),
                  'mes':p['_criado'].strftime('%Y-%m'),'dia':p['_criado'].strftime('%Y-%m-%d'),
                  'canal':p['canal'],'categoria':p['categoria'],'itens':p['_itens'],
                  'valor_centavos':p['_centavos'],'valor_pago_centavos':pago,
                  'status_pagamento':status,'expedido_em':enviado_em,
                  'horas_ate_expedicao':horas,'tem_excecao':bool(problemas),
                  'qtd_excecoes':len(problemas),'motivos_excecao':problemas}
        registros.append(registro)
        for problema in problemas:
            excecoes.append({'pedido_id':codigo,'mes':registro['mes'],'canal':p['canal'],
                             'tipo':problema,'prioridade':'Alta' if problema in ('Divergência de valor','Pagamento ausente','Expedição anterior ao pedido') else 'Média',
                             'valor_centavos':p['_centavos']})
    # Indicadores consolidados, com denominadores explícitos.
    confirmados=[p for p in registros if p['status_pagamento']=='confirmado']
    despachados=[p for p in confirmados if p['horas_ate_expedicao'] is not None and p['horas_ate_expedicao']>=0]
    no_prazo=[p for p in despachados if p['horas_ate_expedicao']<=SLA_HORAS]
    conc_ok=[p for p in confirmados if 'Divergência de valor' not in p['motivos_excecao'] and 'Valor pago inválido' not in p['motivos_excecao']]
    receita_centavos=sum(p['valor_centavos'] for p in conc_ok)
    conciliados_ids={p['pedido_id'] for p in conc_ok}
    grupo=defaultdict(lambda: {'pedidos':0,'confirmados':0,'despachados':0,'no_prazo':0,'excecoes':0,'valor_centavos':0})
    for p in registros:
        for chave in [('mes',p['mes']),('canal',p['canal']),('categoria',p['categoria'])]:
            g=grupo[chave]
            g['pedidos']+=1; g['confirmados']+=int(p['status_pagamento']=='confirmado')
            expedido=p['status_pagamento']=='confirmado' and p['horas_ate_expedicao'] is not None and p['horas_ate_expedicao']>=0
            g['despachados']+=int(expedido)
            g['no_prazo']+=int(expedido and p['horas_ate_expedicao']<=SLA_HORAS)
            g['excecoes']+=int(p['tem_excecao'])
            g['valor_centavos']+=p['valor_centavos'] if p['pedido_id'] in conciliados_ids else 0
    resumo={
        'metadados':{'titulo':'Automação de Operações Multicanal','natureza':'ESTUDO DEMONSTRATIVO · DADOS 100% SINTÉTICOS',
                    'seed':20261108,'referencia':'2026-11-01T00:00:00','sla_horas':SLA_HORAS,
                    'avisos':['Dados totalmente fictícios. Nenhum número representa performance profissional real.',
                              'IA generativa é integração opcional: sem API configurada, os diagnósticos são determinísticos.']},
        'qualidade':{'linhas_brutas':len(pedidos_orig),'linhas_validas':len(pedidos),'linhas_rejeitadas':len(rejeitados),
                     'pagamentos_brutos':len(pagamentos_raw),'expedicoes_brutas':len(expedicoes_raw),
                     'erros_fontes_adicionais':dict(infra)},
        'kpis':{'pedidos_validos':len(registros),'confirmados':len(confirmados),'despachados':len(despachados),
                'expedidos_no_prazo':len(no_prazo),'sla_pct':round(100*len(no_prazo)/len(despachados),2) if despachados else 0,
                'pedidos_com_excecao':sum(p['tem_excecao'] for p in registros),'taxa_excecao_pct':round(100*sum(p['tem_excecao'] for p in registros)/len(registros),2) if registros else 0,
                'pagamentos_conciliados':len(conc_ok),'receita_conciliada_centavos':receita_centavos,
                'motivos_excecao':dict(Counter(e['tipo'] for e in excecoes))},
        'series':{'mensais':[{'chave':k[1],**v} for k,v in sorted(grupo.items()) if k[0]=='mes'],
                  'canais':[{'chave':k[1],**v} for k,v in sorted(grupo.items()) if k[0]=='canal'],
                  'categorias':[{'chave':k[1],**v} for k,v in sorted(grupo.items()) if k[0]=='categoria']},
        'registros':registros,'excecoes':excecoes[:5000]}
    saida.mkdir(parents=True,exist_ok=True)
    salvar_csv(saida/'linhas_rejeitadas.csv',rejeitados,['linha','pedido_id','motivo'])
    salvar_csv(saida/'pedidos_processados.csv', [{**r,'motivos_excecao':' | '.join(r['motivos_excecao'])} for r in registros],
               ['pedido_id','criado_em','mes','dia','canal','categoria','itens','valor_centavos','valor_pago_centavos','status_pagamento','expedido_em','horas_ate_expedicao','tem_excecao','qtd_excecoes','motivos_excecao'])
    salvar_csv(saida/'excecoes.csv',excecoes,['pedido_id','mes','canal','tipo','prioridade','valor_centavos'])
    (saida/'indicadores.json').write_text(json.dumps(resumo,ensure_ascii=False,indent=2),encoding='utf-8')
    return resumo

if __name__=='__main__':
    raiz=Path(__file__).resolve().parent.parent
    print(json.dumps(processar(raiz/'dados'/'brutos',raiz/'dados'/'processados')['kpis'],ensure_ascii=False,indent=2))
