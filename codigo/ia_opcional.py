"""Integração REAL e opcional com a Responses API.
Nunca é chamada pelo pipeline padrão: requer chave e modelo configurados.
Somente KPIs agregados sintéticos são enviados. Não há alegação de uso sem execução.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def extrair_texto(resposta: dict) -> str:
    textos=[]
    for item in resposta.get('output',[]):
        if item.get('type')=='message':
            textos.extend(p.get('text','') for p in item.get('content',[]) if p.get('type')=='output_text')
    texto='\n'.join(x for x in textos if x.strip()).strip()
    if not texto: raise ValueError('Resposta sem conteúdo textual')
    return texto


def analisar(indicadores: dict, chave: str, modelo: str, url: str='https://api.openai.com/v1/responses') -> str:
    info={'dados':'100% sintéticos','periodo':'2026-08 a 2026-10',
          'qualidade':indicadores['qualidade'],
          'kpis':indicadores['kpis'],
          'series':indicadores['series']['mensais']}
    instrucoes=(
      'Você é um analista operacional. Dados são 100% sintéticos e agregados. '
      'Faça no máximo 5 observações curtas em português brasileiro, estritamente suportadas pelos números. '
      'Não invente causas, resultados profissionais reais, economia realizada, projeções nem relações causais. '
      'Declare explicitamente que é análise gerada por IA sobre dados fictícios. '
      'Diferencie observação, hipótese e recomendação de validação; destaque denominadores relevantes. '
      'Nenhum dado pessoal, cliente real ou informação confidencial foi enviado.'
    )
    corpo=json.dumps({'model':modelo,'instructions':instrucoes,'input':json.dumps(info,ensure_ascii=False),
                      'store':False,'max_output_tokens':1100},ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request(url,data=corpo,headers={'Authorization':'Bearer '+chave,
                                                        'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=35) as response:
        return extrair_texto(json.loads(response.read().decode('utf-8')))


def main():
    raiz=Path(__file__).resolve().parent.parent
    chave=os.getenv('OPENAI_API_KEY')
    modelo=os.getenv('OPENAI_MODEL')
    if not chave or not modelo:
        sys.exit('Configure OPENAI_API_KEY e OPENAI_MODEL. A integração é opcional e não foi executada.')
    dados=json.loads((raiz/'dados'/'processados'/'indicadores.json').read_text(encoding='utf-8'))
    try: texto=analisar(dados,chave,modelo)
    except (urllib.error.URLError,ValueError,TimeoutError) as e: sys.exit(f'Erro na integração opcional: {e}')
    destino=raiz/'entregaveis'/'analise_ia_opcional.txt'
    destino.write_text('ANÁLISE GERADA POR IA · DADOS 100% FICTÍCIOS\n\n'+texto,encoding='utf-8')
    print('Análise de IA salva em:',destino)

if __name__=='__main__': main()
