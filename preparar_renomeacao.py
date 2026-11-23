"""Sorteia o subconjunto do teste de renomeação e grava os casos renomeados.

Uso: python preparar_renomeacao.py

Sorteia, com semente fixa, 5 casos vulneráveis e 5 não vulneráveis por CWE
(40 no total) dentre os 120 da amostra, aplica renomeacao.renomear() ao código
já anonimizado e grava:
  dados/casos_renomeados/<caso>.java
  dados/renomeacao.csv            (mesmas colunas de amostra.csv, conjunto "renomeacao")
  dados/renomeacao_mapas.json     (nome original -> nome novo, por caso)
"""

import csv
import hashlib
import json
import random

from config import ARQ_AMOSTRA, DIR_DADOS, RENOMEACAO_POR_ROTULO, SEMENTE_RENOMEACAO
from renomeacao import renomear

DIR_RENOMEADOS = DIR_DADOS / "casos_renomeados"
ARQ_RENOMEACAO = DIR_DADOS / "renomeacao.csv"
ARQ_MAPAS = DIR_DADOS / "renomeacao_mapas.json"


def main() -> None:
    with ARQ_AMOSTRA.open(encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        campos = leitor.fieldnames
        amostra = [c for c in leitor if c["conjunto"] == "amostra"]

    rng = random.Random(SEMENTE_RENOMEACAO)
    sorteados = []
    for categoria in sorted({c["categoria"] for c in amostra}):
        for rotulo in ("VULNERAVEL", "NAO_VULNERAVEL"):
            grupo = sorted((c for c in amostra
                            if c["categoria"] == categoria and c["rotulo_real"] == rotulo),
                           key=lambda c: c["caso"])
            sorteados += rng.sample(grupo, RENOMEACAO_POR_ROTULO)

    DIR_RENOMEADOS.mkdir(parents=True, exist_ok=True)
    linhas, mapas = [], {}
    for caso in sorted(sorteados, key=lambda c: c["caso"]):
        codigo = (DIR_DADOS / caso["arquivo"]).read_text(encoding="utf-8")
        novo, mapa = renomear(codigo)
        destino = DIR_RENOMEADOS / f"{caso['caso']}.java"
        destino.write_text(novo, encoding="utf-8", newline="\n")
        mapas[caso["caso"]] = mapa
        linhas.append({**caso, "conjunto": "renomeacao",
                       "arquivo": destino.relative_to(DIR_DADOS).as_posix(),
                       "sha256": hashlib.sha256(novo.encode("utf-8")).hexdigest(),
                       "linhas": novo.count("\n")})

    with ARQ_RENOMEACAO.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    ARQ_MAPAS.write_text(json.dumps(mapas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(linhas)} casos renomeados em {DIR_RENOMEADOS}")


if __name__ == "__main__":
    main()
