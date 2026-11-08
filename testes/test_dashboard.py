"""Regressões mínimas do frontend compilado e consistência dos dados."""
import json
import re
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'codigo'))
from gerar_dashboard import construir

class TestarDashboard(unittest.TestCase):
    def test_compilacao_reproduzivel(self):
        html=construir(ROOT).read_text(encoding='utf-8')
        for token in ('view-gerencial','view-operacional','view-engenharia','opRows','exportCSV', 'DADOS SINTÉTICOS'):
            self.assertIn(token, html.upper() if token == 'DADOS SINTÉTICOS' else html)
        self.assertNotIn('__INLINE_',html)
        self.assertNotIn('__EMBEDDED_DATA__',html)
        self.assertNotIn('https://cdn.',html)
        self.assertEqual(html,(ROOT/'entregaveis'/'dashboard_offline.html').read_text(encoding='utf-8'))

    def test_payload_equivale_a_processamento(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        result=re.search(r'const DATA=(\{.*?\});</script>',html,re.DOTALL)
        self.assertIsNotNone(result)
        actual=json.loads(result.group(1));raw=json.loads((ROOT/'dados'/'processados'/'indicadores.json').read_text(encoding='utf-8'))
        self.assertEqual(len(actual['registros']),raw['kpis']['pedidos_validos'])
        self.assertEqual(actual['qualidade'],raw['qualidade'])
        self.assertEqual(sum(bool(r['e']) for r in actual['registros']),raw['kpis']['pedidos_com_excecao'])
        self.assertEqual(sum(r['v'] for r in actual['registros'] if r['s']=='confirmado' and abs(r['p']-r['v'])<=1),raw['kpis']['receita_conciliada_centavos'])

if __name__ == '__main__':unittest.main()
