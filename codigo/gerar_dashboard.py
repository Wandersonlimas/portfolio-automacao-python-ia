"""Compila código-fonte web separado em HTML estático, autossuficiente e auditável."""
from __future__ import annotations
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
WEB = BASE / 'src' / 'web'


def construir(raiz: Path) -> Path:
    raiz = Path(raiz)
    dados = json.loads((raiz/'dados'/'processados'/'indicadores.json').read_text(encoding='utf-8'))
    registros = [
        {'i':r['pedido_id'], 'd':r['dia'], 'm':r['mes'], 'c':r['canal'],
         'g':r['categoria'], 's':r['status_pagamento'], 'v':r['valor_centavos'],
         'p':r['valor_pago_centavos'], 'h':r['horas_ate_expedicao'], 'e':r['motivos_excecao']}
        for r in dados['registros']
    ]
    payload = {'registros': registros, 'qualidade': dados['qualidade'],
               'meta': {'sla_horas': dados['metadados']['sla_horas'],
                        'natureza': dados['metadados']['natureza']}}
    serialized = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    template = (WEB/'templates'/'dashboard.html').read_text(encoding='utf-8')
    css = (WEB/'css'/'dashboard.css').read_text(encoding='utf-8')
    js = (WEB/'js'/'dashboard.js').read_text(encoding='utf-8')
    assert all(template.count(token) == 1 for token in ['__INLINE_CSS__','__EMBEDDED_DATA__','__INLINE_JS__'])
    html = template.replace('__INLINE_CSS__', css).replace('__EMBEDDED_DATA__', serialized).replace('__INLINE_JS__', js)
    assert '__EMBEDDED_DATA__' not in html
    (raiz/'index.html').write_text(html, encoding='utf-8')
    (raiz/'entregaveis'/'dashboard_offline.html').write_text(html, encoding='utf-8')
    return raiz/'index.html'

if __name__ == '__main__':
    print(construir(BASE))
