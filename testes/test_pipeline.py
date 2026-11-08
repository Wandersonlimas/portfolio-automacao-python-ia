import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'codigo'))
from gerar_dados import gerar
from pipeline import centavos,data_iso,limpar_pedidos,processar
from insights import gerar_insights
from ia_opcional import extrair_texto

class TestesTecnicos(unittest.TestCase):
    def test_centavos_exatos(self):
        self.assertEqual(centavos('12.34'),1234)
        self.assertEqual(centavos('10.005'),1001)
        with self.assertRaises(ValueError): centavos('NaN')
        with self.assertRaises(ValueError): centavos('abc')

    def test_regras_quarentena(self):
        base={'pedido_id':'X','criado_em':'2026-09-01T10:00','canal':'Site próprio','categoria':'Jeans','itens':'1','valor_brl':'99.99'}
        rows=[base,dict(base),{**base,'pedido_id':'Y','valor_brl':'-5'}, {**base,'pedido_id':'Z','criado_em':'n/a'}]
        ok,erro=limpar_pedidos(rows)
        self.assertEqual(len(ok),1)
        self.assertEqual(len(erro),3)
        self.assertEqual({x['motivo'] for x in erro},{'ID duplicado','Valor não positivo','Campo ou tipo inválido'})

    def test_semente_reproduzivel(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            gerar(Path(a),150);gerar(Path(b),150)
            for nome in ('pedidos.csv','pagamentos.csv','expedicoes.csv'):
                self.assertEqual((Path(a)/nome).read_bytes(),(Path(b)/nome).read_bytes())

    def test_integracao_e_denominadores(self):
        with tempfile.TemporaryDirectory() as d:
            raiz=Path(d);gerar(raiz/'brutos',500);out=processar(raiz/'brutos',raiz/'processados')
            k=out['kpis'];q=out['qualidade'];r=out['registros']
            self.assertEqual(q['linhas_validas'],len(r))
            self.assertEqual(k['pedidos_validos'],len(r))
            self.assertEqual(k['despachados'],sum(x['status_pagamento']=='confirmado' and x['horas_ate_expedicao'] is not None and x['horas_ate_expedicao']>=0 for x in r))
            self.assertEqual(k['expedidos_no_prazo'],sum(x['status_pagamento']=='confirmado' and x['horas_ate_expedicao'] is not None and 0<=x['horas_ate_expedicao']<=48 for x in r))
            self.assertLessEqual(k['expedidos_no_prazo'],k['despachados'])
            self.assertGreater(k['pedidos_com_excecao'],0)
            self.assertGreater(q['linhas_rejeitadas'],0)
            self.assertTrue((raiz/'processados'/'excecoes.csv').exists())

    def test_diagnostico_deterministico(self):
        dados={'motivos_excecao':{'SLA de expedição excedido':10},'pedidos_com_excecao':10,'pedidos_validos':200,'taxa_excecao_pct':5,'expedidos_no_prazo':120,'despachados':150,'sla_pct':80}
        r=gerar_insights(dados,[])
        self.assertEqual(len(r),3)
        self.assertIn('10',r[0]['texto'])

    def test_parser_da_resposta_ia_sem_chamada_remota(self):
        resposta={'output':[{'type':'message','content':[{'type':'output_text','text':'Teste de interface local'}]}]}
        self.assertEqual(extrair_texto(resposta),'Teste de interface local')
        with self.assertRaises(ValueError):extrair_texto({'output':[]})

if __name__=='__main__':unittest.main()
