"""Sorteia a amostra estratificada e grava os casos anonimizados.

Uso: python preparar_amostra.py

Saídas:
  dados/amostra.csv      um caso por linha, com conjunto (amostra/piloto), rótulo e hash
  dados/casos/<id>.java  código anonimizado, exatamente como será enviado ao modelo
"""

import csv
import hashlib
import random
import sys
from collections import Counter

from anonimizacao import anonimizar
from config import (ARQ_AMOSTRA, ARQ_GABARITO, CASOS_POR_ROTULO, CWES, DIR_CASOS,
                    DIR_FONTES, PILOTO_POR_ROTULO, SEMENTE_AMOSTRA)


def ler_gabarito() -> list[dict]:
    casos = []
    with ARQ_GABARITO.open(encoding="utf-8") as f:
        for linha in csv.reader(f):
            if not linha or linha[0].lstrip().startswith("#"):
                continue
            nome, categoria, real, cwe = (campo.strip() for campo in linha[:4])
            if categoria not in CWES:
                continue
            if int(cwe) != CWES[categoria][0]:
                sys.exit(f"CWE inesperada para {nome}: {cwe} (categoria {categoria})")
            casos.append({"caso": nome, "categoria": categoria, "cwe": int(cwe),
                          "vulneravel": real.lower() == "true"})
    return casos


def sortear(casos: list[dict]) -> list[dict]:
    rng = random.Random(SEMENTE_AMOSTRA)
    selecionados = []
    for categoria in sorted(CWES):
        for vulneravel in (True, False):
            grupo = sorted(c["caso"] for c in casos
                           if c["categoria"] == categoria and c["vulneravel"] == vulneravel)
            sorteio = rng.sample(grupo, CASOS_POR_ROTULO + PILOTO_POR_ROTULO)
            for posicao, nome in enumerate(sorteio):
                conjunto = "amostra" if posicao < CASOS_POR_ROTULO else "piloto"
                selecionados.append({"caso": nome, "categoria": categoria,
                                     "cwe": CWES[categoria][0],
                                     "rotulo_real": "VULNERAVEL" if vulneravel else "NAO_VULNERAVEL",
                                     "conjunto": conjunto})
    return selecionados


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # console do Windows não é UTF-8 por padrão
    if not ARQ_GABARITO.exists():
        sys.exit(f"Gabarito não encontrado em {ARQ_GABARITO}. Clone o BenchmarkJava (ver README).")

    selecionados = sortear(ler_gabarito())
    DIR_CASOS.mkdir(parents=True, exist_ok=True)

    for caso in selecionados:
        fonte = (DIR_FONTES / f"{caso['caso']}.java").read_text(encoding="utf-8")
        codigo = anonimizar(fonte)
        if "BenchmarkTest" in codigo:
            sys.exit(f"Identificador do caso ainda presente após anonimizar {caso['caso']}")
        destino = DIR_CASOS / f"{caso['caso']}.java"
        destino.write_text(codigo, encoding="utf-8", newline="\n")
        caso["arquivo"] = destino.relative_to(ARQ_AMOSTRA.parent).as_posix()
        caso["sha256"] = hashlib.sha256(codigo.encode("utf-8")).hexdigest()
        caso["linhas"] = codigo.count("\n")

    with ARQ_AMOSTRA.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(selecionados[0]))
        escritor.writeheader()
        escritor.writerows(selecionados)

    contagem = Counter((c["conjunto"], c["categoria"], c["rotulo_real"]) for c in selecionados)
    for chave in sorted(contagem):
        print(*chave, contagem[chave], sep="\t")
    print(f"{len(selecionados)} casos gravados em {ARQ_AMOSTRA}")


if __name__ == "__main__":
    main()
