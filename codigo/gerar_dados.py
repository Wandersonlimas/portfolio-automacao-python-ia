"""Geração 100% sintética de dados operacionais para demonstração."""
from __future__ import annotations
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20261108
CANAIS = ('Marketplace A', 'Marketplace B', 'Site próprio')
CATEGORIAS = ('Moda casual', 'Fitness', 'Acessórios', 'Jeans')


def gravar(path: Path, campos: list[str], linhas: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=campos, extrasaction='ignore', delimiter=';')
        writer.writeheader()
        writer.writerows(linhas)


def gerar(base: Path, quantidade: int = 5400) -> dict:
    """Gera 3 bases, com anomalias intencionais e regras reproduzíveis."""
    rng = random.Random(SEED)
    base = Path(base)
    pedidos, pagamentos, expedicoes = [], [], []
    inicio = datetime(2026, 8, 1, 8)
    fim = datetime(2026, 10, 31, 20)
    duracao = int((fim - inicio).total_seconds() // 60)
    for numero in range(1, quantidade + 1):
        oid = f'PED-{numero:06d}'
        criado = inicio + timedelta(minutes=rng.randint(0, duracao))
        canal = rng.choices(CANAIS, weights=[45, 35, 20], k=1)[0]
        categoria = rng.choices(CATEGORIAS, weights=[39, 24, 13, 24], k=1)[0]
        quantidade_itens = rng.randint(1, 4)
        total_centavos = int(rng.randint(4900, 30900) * quantidade_itens)
        valor = f'{total_centavos/100:.2f}'
        pedidos.append({'pedido_id': oid, 'criado_em': criado.isoformat(timespec='minutes'),
                        'canal': canal, 'categoria': categoria, 'itens': quantidade_itens,
                        'valor_brl': valor})
        # Erros intencionais tratados pelo ETL, nunca usados como fatos de empresas.
        if numero % 193 == 0:
            pedidos[-1]['valor_brl'] = '-15.00'
        if numero % 257 == 0:
            pedidos[-1]['criado_em'] = 'data_inválida'
        if numero % 283 == 0:
            pedidos[-1]['canal'] = ''
        if numero % 173 == 0:
            pedidos.append(dict(pedidos[-1]))
        status = rng.choices(('confirmado', 'pendente', 'recusado'), weights=[90, 6, 4], k=1)[0]
        diferenca = rng.choice([-430, 210, 560]) if numero % 91 == 0 else 0
        if numero % 107 != 0:
            pagamentos.append({'pedido_id': oid, 'status_pagamento': status,
                               'valor_pago_brl': f'{(total_centavos+diferenca)/100:.2f}' if status == 'confirmado' else '0.00',
                               'confirmado_em': (criado + timedelta(minutes=rng.randint(2, 180))).isoformat(timespec='minutes') if status == 'confirmado' else ''})
        if status == 'confirmado' and rng.random() < 0.95:
            # Atrasos variáveis, 48 horas é o SLA didático do estudo.
            horas = rng.choices((rng.randint(4, 33), rng.randint(49, 92)), weights=[83, 17], k=1)[0]
            despacho = criado + timedelta(hours=horas, minutes=rng.randint(0, 59))
            expedicoes.append({'pedido_id': oid, 'expedido_em': despacho.isoformat(timespec='minutes'),
                               'transportadora': rng.choice(('Operador Logístico A', 'Operador Logístico B', 'Operador Logístico C'))})
    gravar(base/'pedidos.csv', ['pedido_id', 'criado_em', 'canal', 'categoria', 'itens', 'valor_brl'], pedidos)
    gravar(base/'pagamentos.csv', ['pedido_id', 'status_pagamento', 'valor_pago_brl', 'confirmado_em'], pagamentos)
    gravar(base/'expedicoes.csv', ['pedido_id', 'expedido_em', 'transportadora'], expedicoes)
    return {'pedidos_brutos': len(pedidos), 'pagamentos': len(pagamentos), 'expedicoes': len(expedicoes), 'seed': SEED}


if __name__ == '__main__':
    print(gerar(Path(__file__).resolve().parent.parent/'dados'/'brutos'))
