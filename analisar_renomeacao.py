"""Análise do teste de renomeação (contaminação), definido após a coleta principal.

Uso: python analisar_renomeacao.py

Compara, nos 40 casos de dados/renomeacao.csv e na condição zero-shot, as
execuções da coleta original (resultados/amostra.jsonl) com as dos mesmos casos
renomeados (resultados/renomeacao.jsonl). Se o acerto depender de memorização
dos casos do benchmark, ele deve cair com a renomeação. Grava
analise/renomeacao.json.
"""

import csv
import json
import sys

import numpy as np

from analisar import FINAIS, VULN, acerto_majoritario, concordancia, mcnemar_exato, razao
from config import CONDICOES_RENOMEACAO, DIR_ANALISE, DIR_DADOS, DIR_RESULTADOS, K_REPETICOES


def vereditos(arquivo, casos: set, condicao: str) -> dict:
    por_caso = {c: [] for c in casos}
    with arquivo.open(encoding="utf-8") as f:
        for linha in f:
            r = json.loads(linha)
            if r["caso"] in casos and r["condicao"] == condicao and r["status"] in FINAIS:
                por_caso[r["caso"]].append(r.get("veredito"))
    return por_caso


def medidas(por_caso: dict, rotulos: dict) -> dict:
    tp = fp = fn = tn = abst = 0
    for caso, vs in por_caso.items():
        for v in vs:
            if v is None:
                abst += 1
            elif rotulos[caso] == VULN:
                tp, fn = tp + (v == VULN), fn + (v != VULN)
            else:
                fp, tn = fp + (v == VULN), tn + (v != VULN)
    tpr, esp = razao(tp, tp + fn), razao(tn, tn + fp)
    validos = {c: [v for v in vs if v is not None] for c, vs in por_caso.items()}
    acertos = {c: acerto_majoritario(vs, rotulos[c])[0] for c, vs in validos.items()}
    concs = [x for x in (concordancia(vs) for vs in validos.values()) if x is not None]
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "abstencoes": abst,
            "revocacao": tpr, "especificidade": esp,
            "tpr_menos_fpr": None if tpr is None or esp is None else tpr + esp - 1,
            "casos_corretos": sum(acertos.values()),
            "concordancia_media": float(np.mean(concs)) if concs else None,
            "acertos": acertos}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    with (DIR_DADOS / "renomeacao.csv").open(encoding="utf-8") as f:
        rotulos = {c["caso"]: c["rotulo_real"] for c in csv.DictReader(f)}
    casos = sorted(rotulos)
    arq_ren = DIR_RESULTADOS / "renomeacao.jsonl"
    if not arq_ren.exists():
        sys.exit("resultados/renomeacao.jsonl não existe. Rode: python coletar.py --conjunto renomeacao")

    resultado = {"n_casos": len(casos), "k": K_REPETICOES, "condicoes": {}}
    for cond in CONDICOES_RENOMEACAO:
        orig = vereditos(DIR_RESULTADOS / "amostra.jsonl", set(casos), cond)
        ren = vereditos(arq_ren, set(casos), cond)
        faltando = sum(K_REPETICOES - len(v) for v in ren.values())
        if faltando:
            sys.exit(f"Coleta de renomeação incompleta: faltam {faltando} execuções.")
        mo, mr = medidas(orig, rotulos), medidas(ren, rotulos)
        a = np.array([mo["acertos"][c] for c in casos])
        b = np.array([mr["acertos"][c] for c in casos])
        teste = mcnemar_exato(a, b)  # primeira = original, segunda = renomeado
        mudaram = [c for c in casos if mo["acertos"][c] != mr["acertos"][c]]
        for m in (mo, mr):
            m.pop("acertos")
        resultado["condicoes"][cond] = {"original": mo, "renomeado": mr,
                                        "mcnemar": teste, "casos_que_mudaram": mudaram}
        print(f"\n{cond} ({len(casos)} casos, K={K_REPETICOES})")
        for nome, m in (("original", mo), ("renomeado", mr)):
            print(f"  {nome:10s} corretos={m['casos_corretos']:2d}  TP={m['tp']} FP={m['fp']} "
                  f"FN={m['fn']} TN={m['tn']} abst={m['abstencoes']}  "
                  f"TPR-FPR={m['tpr_menos_fpr']:.3f}  conc={m['concordancia_media']:.3f}")
        print(f"  McNemar exato: só original acerta={teste['so_primeira_acerta']}, "
              f"só renomeado acerta={teste['so_segunda_acerta']}, p={teste['p']:.3f}")

    DIR_ANALISE.mkdir(parents=True, exist_ok=True)
    (DIR_ANALISE / "renomeacao.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
