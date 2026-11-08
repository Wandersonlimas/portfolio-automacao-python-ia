"""Orquestrador. Execução totalmente offline, determinística e auditável."""
from pathlib import Path
import json
from gerar_dados import gerar
from pipeline import processar
from gerar_dashboard import construir
from gerar_relatorio import relatorio


def main():
    raiz=Path(__file__).resolve().parent.parent
    fontes=gerar(raiz/'dados'/'brutos')
    dados=processar(raiz/'dados'/'brutos',raiz/'dados'/'processados')
    html=construir(raiz)
    pdf=relatorio(raiz, dados)
    print(json.dumps({'fontes':fontes,'kpis':dados['kpis'],'html':str(html),'pdf':str(pdf)},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
