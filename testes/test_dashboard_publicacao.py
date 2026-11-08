"""Validação estática do dashboard publicado, com teste de sintaxe JavaScript."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if 'id' in d: self.ids.append(d['id'])
        if tag=='a' and 'href' in d:self.links.append(d['href'])

class TestDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'index.html').read_text(encoding='utf-8')
    def test_estrutura(self):
        self.assertIn('<!doctype html>',self.html[:100].lower())
        self.assertIn('viewport',self.html)
        parser=Parser();parser.feed(self.html)
        self.assertEqual(len(parser.ids),len(set(parser.ids)),'IDs HTML duplicados')
        self.assertGreater(len(parser.ids),10)
    def test_scripts_e_dados(self):
        matches=list(re.finditer(r'<script([^>]*)>([\s\S]*?)</script>',self.html,re.I))
        self.assertEqual(len(matches),2)
        js=[]
        for m in matches:
            attrs=m.group(1)
            body=m.group(2).strip()
            if 'application/json' in attrs:
                data=json.loads(body)
                self.assertTrue(data.get('registros'))
                self.assertTrue(data.get('meta'))
            elif body.startswith('const DATA='):
                data=json.loads(body[len('const DATA='):].rstrip(';').strip())
                self.assertTrue(data.get('registros'))
                self.assertTrue(data.get('meta'))
                js.append(m.group(2))
            else:
                js.append(m.group(2))
        self.assertTrue(js)
        if shutil.which('node'):
            for src in js:
                with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8') as f:
                    f.write(src);f.flush()
                    subprocess.run(['node','--check',f.name],check=True,capture_output=True,text=True)
    def test_filtros_e_navegacao(self):
        for element in ["fMonth","fChannel","fCategory","fStatus","fReason","clearFilters"]:
            self.assertIn('id="'+element+'"',self.html)
        self.assertIn('100%',self.html)

if __name__=='__main__':
    unittest.main()
