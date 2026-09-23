#!/usr/bin/env python3
"""Simulador de dados de estoque de supermercado.

Cada execução gera N registros (padrão 20) e os ACRESCENTA ao CSV de saída,
sem apagar execuções anteriores.

Uso:
    python3 simulador.py [--registros 20] [--saida caminho/estoque.csv]

Por padrão grava em ../dados/estoque.csv (relativo ao script) ou em
$DADOS_DIR/estoque.csv se a variável de ambiente existir.
"""
import argparse
import csv
import os
import random
import uuid
from datetime import datetime
from pathlib import Path

PRODUTOS = [
    ("P001", "Arroz 5kg", "Mercearia", 27.90, 30),
    ("P002", "Feijão 1kg", "Mercearia", 8.50, 40),
    ("P003", "Leite integral 1L", "Laticínios", 5.20, 60),
    ("P004", "Iogurte natural", "Laticínios", 3.80, 45),
    ("P005", "Banana prata kg", "Hortifrúti", 6.90, 35),
    ("P006", "Tomate kg", "Hortifrúti", 8.90, 25),
    ("P007", "Peito de frango kg", "Açougue", 18.90, 30),
    ("P008", "Pão francês kg", "Padaria", 16.00, 20),
    ("P009", "Refrigerante 2L", "Bebidas", 9.50, 50),
    ("P010", "Detergente 500ml", "Limpeza", 2.90, 70),
]

CAMPOS = [
    "id_registro", "data_hora", "id_produto", "produto", "categoria",
    "preco_unitario", "estoque_atual", "estoque_minimo",
    "vendas_dia", "dias_ate_validade",
]


def gerar_registro(agora: datetime) -> dict:
    id_prod, nome, categoria, preco, minimo = random.choice(PRODUTOS)
    perecivel = categoria in {"Laticínios", "Hortifrúti", "Açougue", "Padaria"}
    return {
        "id_registro": str(uuid.uuid4()),
        "data_hora": agora.isoformat(timespec="seconds"),
        "id_produto": id_prod,
        "produto": nome,
        "categoria": categoria,
        "preco_unitario": round(preco * random.uniform(0.95, 1.05), 2),
        "estoque_atual": random.randint(0, minimo * 3),
        "estoque_minimo": minimo,
        "vendas_dia": random.randint(0, minimo * 2),
        "dias_ate_validade": random.randint(1, 10) if perecivel else random.randint(30, 365),
    }


def caminho_padrao() -> Path:
    base = os.environ.get("DADOS_DIR")
    pasta = Path(base) if base else Path(__file__).resolve().parent.parent / "dados"
    return pasta / "estoque.csv"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registros", type=int, default=20)
    ap.add_argument("--saida", type=Path, default=caminho_padrao())
    args = ap.parse_args()

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    novo_arquivo = not args.saida.exists()
    agora = datetime.now()
    total = max(args.registros, 10)

    with args.saida.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if novo_arquivo:
            w.writeheader()
        for _ in range(total):
            w.writerow(gerar_registro(agora))

    print(f"{total} registros gravados em {args.saida}")


if __name__ == "__main__":
    main()
