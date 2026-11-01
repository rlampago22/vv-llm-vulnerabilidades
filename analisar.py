"""Análise pré-especificada dos resultados (Seções 2.4 e 4.5 do artigo).

Uso: python analisar.py

Lê resultados/amostra.jsonl e dados/amostra.csv e grava em analise/:
  resumo.json   todas as métricas e testes
  tabelas.tex   tabelas da Seção 5
e imprime o resumo no terminal.

Regras de agregação:
- Desempenho por execução: cada resposta válida é uma classificação; abstenções
  ficam fora do F1 e entram na cobertura (F1 efetivo = F1 x cobertura).
- Intervalos de 95% por bootstrap percentil, reamostrando casos (não execuções),
  com os mesmos índices para todas as condições.
- Voto majoritário por (caso, condição) sobre as execuções válidas. Empate, ou
  nenhuma execução válida, conta como erro (regra conservadora); o número de
  empates é reportado.
- Concordância por pares só com K >= 2 execuções válidas; senão, indefinida.

As chaves "exploratorio" e "complementar" do resumo ficam fora dos testes
pré-especificados: a primeira foi definida após a coleta; a segunda, após as
revisões do artigo (especificidade, MCC, diferenças pareadas de F1, quebra por
CWE e associação entre rótulo e system_fingerprint).
"""

import csv
import json
import re
import sys
from collections import Counter
from itertools import combinations

import numpy as np
from scipy import stats

from config import (ALFA, ARQ_AMOSTRA, DIR_ANALISE, DIR_RESULTADOS, K_REPETICOES,
                    N_BOOTSTRAP, N_PERMUTACOES, PREVALENCIA_TRIAGEM, SEMENTE_BOOTSTRAP,
                    SEMENTE_PERMUTACAO)
from prompts import CONDICOES

ESTRATEGIAS = ("zero_shot", "cot", "fluxo")
NOMES = {"zero_shot": "Zero-shot", "cot": "CoT", "fluxo": "Fluxo de dados",
         "fluxo_skill": "Fluxo de dados + \\textit{skill}"}
FINAIS = ("valido", "abstencao", "filtro")
VULN = "VULNERAVEL"

# Análise exploratória pós-coleta (Seção 5.5): mecanismo com que o benchmark
# neutraliza o fluxo nos casos não vulneráveis, reconhecido por padrões textuais.
_RE_CONSTANTE = re.compile(r'"(item|moreitem|alsoitem|item!)"|ItemStuff')
_RE_CONDICAO_FIXA = re.compile(r"switchTarget|\(7 \* 42\)|num \* 42|\(500 / 42\)")


# ---------------------------------------------------------------- leitura

def carregar() -> tuple[dict, list[str], list[dict]]:
    with ARQ_AMOSTRA.open(encoding="utf-8") as f:
        rotulos = {c["caso"]: c["rotulo_real"] for c in csv.DictReader(f)
                   if c["conjunto"] == "amostra"}
    registros = {}
    with (DIR_RESULTADOS / "amostra.jsonl").open(encoding="utf-8") as f:
        for linha in f:
            r = json.loads(linha)
            if r["status"] in FINAIS:  # linhas erro_api ficam só como registro
                registros[r["id"]] = r
    esperado = len(rotulos) * len(CONDICOES) * K_REPETICOES
    if len(registros) != esperado:
        sys.exit(f"Coleta incompleta: {len(registros)} de {esperado} requisições concluídas.")
    return rotulos, sorted(rotulos), list(registros.values())


# ---------------------------------------------------------------- métricas

def razao(num, den):
    return num / den if den else None


def prf(tp, fp, fn):
    return razao(tp, tp + fp), razao(tp, tp + fn), razao(2 * tp, 2 * tp + fp + fn)


def matriz_por_caso(vereditos: dict, rotulos: dict, casos: list[str]) -> np.ndarray:
    """Contagens de TP, FP, FN, TN por caso, somando as execuções válidas."""
    m = np.zeros((len(casos), 4), dtype=int)
    for i, caso in enumerate(casos):
        vulneravel = rotulos[caso] == VULN
        for v in vereditos[caso]:
            if v == VULN:
                m[i, 0 if vulneravel else 1] += 1
            else:
                m[i, 2 if vulneravel else 3] += 1
    return m


def ic_bootstrap(m: np.ndarray, indices: np.ndarray) -> dict:
    tp, fp, fn, _ = m[indices].sum(axis=1).T.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        amostras = {"precisao": tp / (tp + fp), "revocacao": tp / (tp + fn),
                    "f1": 2 * tp / (2 * tp + fp + fn)}
    return {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]
            for k, v in amostras.items()}


def concordancia(vs: list[str]):
    k = len(vs)
    if k < 2:
        return None
    nv = vs.count(VULN)
    nn = k - nv
    return (nv * (nv - 1) + nn * (nn - 1)) / (k * (k - 1))


def acerto_majoritario(vs: list[str], rotulo: str) -> tuple[int, bool]:
    nv = vs.count(VULN)
    nn = len(vs) - nv
    if nv == nn:  # empate ou nenhuma execução válida
        return 0, True
    return int((VULN if nv > nn else "NAO_VULNERAVEL") == rotulo), False


def media(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def resumo_estabilidade(concs: dict, rotulos: dict, filtro=None) -> dict:
    valores = [c for caso, c in concs.items()
               if c is not None and (filtro is None or rotulos[caso] == filtro)]
    return {"n_casos": len(valores), "media": media(valores),
            "prop_unanimes": razao(sum(v == 1 for v in valores), len(valores))}


# ---------------------------------------------------------------- testes

def cochran_q(x: np.ndarray) -> dict:
    n, k = x.shape
    col = x.sum(axis=0)
    lin = x.sum(axis=1)
    total = x.sum()
    den = k * total - (lin ** 2).sum()
    if den == 0:
        return {"estatistica": None, "gl": k - 1, "p": None}
    q = (k - 1) * (k * (col ** 2).sum() - total ** 2) / den
    return {"estatistica": float(q), "gl": k - 1, "p": float(stats.chi2.sf(q, k - 1))}


def mcnemar_exato(a: np.ndarray, b: np.ndarray) -> dict:
    so_a = int(((a == 1) & (b == 0)).sum())
    so_b = int(((a == 0) & (b == 1)).sum())
    p = stats.binomtest(so_a, so_a + so_b, 0.5).pvalue if so_a + so_b else 1.0
    return {"so_primeira_acerta": so_a, "so_segunda_acerta": so_b, "p": float(p)}


def wilcoxon(x, y) -> dict:
    if all(a == b for a, b in zip(x, y)):  # sem diferenças: teste indefinido
        return {"n": len(x), "estatistica": None, "p": None, "nota": "sem diferenças"}
    res = stats.wilcoxon(x, y)
    return {"n": len(x), "estatistica": float(res.statistic), "p": float(res.pvalue)}


def holm(ps: list) -> list:
    validos = [(p, i) for i, p in enumerate(ps) if p is not None]
    ajustados = [None] * len(ps)
    acumulado = 0.0
    for posicao, (p, i) in enumerate(sorted(validos)):
        acumulado = max(acumulado, min(1.0, (len(validos) - posicao) * p))
        ajustados[i] = acumulado
    return ajustados


def pareados(concs: dict, a: str, b: str) -> tuple[list, list]:
    casos = [c for c in concs[a] if concs[a][c] is not None and concs[b][c] is not None]
    return [concs[a][c] for c in casos], [concs[b][c] for c in casos]


# ---------------------------------------------------------------- análise

def analisar() -> dict:
    rotulos, casos, registros = carregar()
    vereditos = {c: {caso: [] for caso in casos} for c in CONDICOES}
    status = {c: Counter() for c in CONDICOES}
    motivos = {c: Counter() for c in CONDICOES}
    fingerprints = {c: Counter() for c in CONDICOES}
    acerto_fp = {c: Counter() for c in CONDICOES}
    for r in registros:
        c = r["condicao"]
        status[c][r["status"]] += 1
        if r["status"] == "abstencao":
            motivos[c][r["motivo"]] += 1
        if r["status"] == "valido":
            vereditos[c][r["caso"]].append(r["veredito"])
            fp = r.get("system_fingerprint")
            fingerprints[c][fp] += 1
            acerto_fp[c][fp] += r["veredito"] == r["rotulo_real"]

    rng = np.random.default_rng(SEMENTE_BOOTSTRAP)
    indices = rng.integers(0, len(casos), size=(N_BOOTSTRAP, len(casos)))

    resultado = {"n_casos": len(casos), "k": K_REPETICOES, "n_bootstrap": N_BOOTSTRAP,
                 "condicoes": {}, "testes": {}}
    acertos, concs, matrizes = {}, {}, {}
    for c in CONDICOES:
        m = matrizes[c] = matriz_por_caso(vereditos[c], rotulos, casos)
        tp, fp, fn, tn = (int(v) for v in m.sum(axis=0))
        p, r, f1 = prf(tp, fp, fn)
        total = sum(status[c].values())
        abstencao = status[c]["abstencao"] / total
        cobertura = 1 - abstencao
        votos = [acerto_majoritario(vereditos[c][caso], rotulos[caso]) for caso in casos]
        acertos[c] = np.array([v for v, _ in votos])
        concs[c] = {caso: concordancia(vereditos[c][caso]) for caso in casos}
        resultado["condicoes"][c] = {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precisao": p, "revocacao": r, "f1": f1,
            "ic95": ic_bootstrap(m, indices),
            "execucoes": total, "status": dict(status[c]), "motivos_abstencao": dict(motivos[c]),
            "taxa_abstencao": abstencao, "cobertura": cobertura,
            "f1_efetivo": f1 * cobertura if f1 is not None else None,
            "distribuicao_k": dict(Counter(len(vereditos[c][caso]) for caso in casos)),
            "voto_majoritario": {"acertos": int(acertos[c].sum()),
                                 "empates": sum(e for _, e in votos)},
            "estabilidade": {
                "geral": resumo_estabilidade(concs[c], rotulos),
                "vulneraveis": resumo_estabilidade(concs[c], rotulos, VULN),
                "nao_vulneraveis": resumo_estabilidade(concs[c], rotulos, "NAO_VULNERAVEL"),
            },
            "por_fingerprint": {fp: {"respostas": n, "acerto": acerto_fp[c][fp] / n}
                                for fp, n in fingerprints[c].items()},
        }

    # Pergunta principal: três estratégias de prompting.
    t = resultado["testes"]
    t["cochran_acerto"] = cochran_q(np.column_stack([acertos[c] for c in ESTRATEGIAS]))
    pares = list(combinations(ESTRATEGIAS, 2))
    mcn = [mcnemar_exato(acertos[a], acertos[b]) for a, b in pares]
    for teste, p_holm in zip(mcn, holm([x["p"] for x in mcn])):
        teste["p_holm"] = p_holm
    t["mcnemar_acerto"] = {f"{a} x {b}": x for (a, b), x in zip(pares, mcn)}

    completos = [caso for caso in casos if all(concs[c][caso] is not None for c in ESTRATEGIAS)]
    colunas = [[concs[c][caso] for caso in completos] for c in ESTRATEGIAS]
    if len({tuple(col) for col in colunas}) == 1:
        t["friedman_concordancia"] = {"n": len(completos), "estatistica": None, "p": None,
                                      "nota": "sem diferenças"}
    else:
        fr = stats.friedmanchisquare(*colunas)
        t["friedman_concordancia"] = {"n": len(completos), "estatistica": float(fr.statistic),
                                      "p": float(fr.pvalue)}
    wil = [wilcoxon(*pareados(concs, a, b)) for a, b in pares]
    for teste, p_holm in zip(wil, holm([x["p"] for x in wil])):
        teste["p_holm"] = p_holm
    t["wilcoxon_concordancia"] = {f"{a} x {b}": x for (a, b), x in zip(pares, wil)}

    # Pergunta exploratória: contraste único fluxo x fluxo_skill (sem ajuste).
    t["skill_mcnemar_acerto"] = mcnemar_exato(acertos["fluxo"], acertos["fluxo_skill"])
    t["skill_wilcoxon_concordancia"] = wilcoxon(*pareados(concs, "fluxo", "fluxo_skill"))

    # Pergunta secundária: vulneráveis x não vulneráveis dentro de cada condição.
    mw = {}
    for c in CONDICOES:
        v = [x for caso, x in concs[c].items() if x is not None and rotulos[caso] == VULN]
        n = [x for caso, x in concs[c].items() if x is not None and rotulos[caso] != VULN]
        res = stats.mannwhitneyu(v, n, alternative="two-sided")
        mw[c] = {"n_vuln": len(v), "n_nao_vuln": len(n), "u": float(res.statistic),
                 "p": float(res.pvalue)}
    for c, p_holm in zip(CONDICOES, holm([mw[c]["p"] for c in CONDICOES])):
        mw[c]["p_holm"] = p_holm
    t["mannwhitney_concordancia_por_rotulo"] = mw
    t["alfa"] = ALFA
    resultado["exploratorio"] = exploratorio(rotulos, casos, registros, vereditos)
    resultado["complementar"] = complementar(rotulos, casos, registros, matrizes,
                                             acertos, concs, indices)
    return resultado


def mecanismo(caso: str) -> str:
    with ARQ_AMOSTRA.open(encoding="utf-8") as f:
        arquivo = next(c["arquivo"] for c in csv.DictReader(f) if c["caso"] == caso)
    codigo = (ARQ_AMOSTRA.parent / arquivo).read_text(encoding="utf-8")
    if _RE_CONSTANTE.search(codigo):
        return "constante"
    return "condicao_fixa" if _RE_CONDICAO_FIXA.search(codigo) else "outro"


def exploratorio(rotulos: dict, casos: list[str], registros: list[dict],
                 vereditos: dict) -> dict:
    """Números citados nas Seções 5.3 a 5.5, fora dos testes pré-especificados."""
    nao_vuln = [caso for caso in casos if rotulos[caso] != VULN]
    grupos = {caso: mecanismo(caso) for caso in nao_vuln}
    fp_por_mecanismo, contagens = {}, {}
    for c in CONDICOES:
        n, fp = Counter(), Counter()
        for caso in nao_vuln:
            n[grupos[caso]] += len(vereditos[c][caso])
            fp[grupos[caso]] += vereditos[c][caso].count(VULN)
        fp_por_mecanismo[c] = {g: fp[g] / n[g] for g in sorted(n)}
        contagens[c] = {g: {"fp": fp[g], "execucoes": n[g]} for g in sorted(n)}
    instaveis = {c: [caso for caso in casos if len(set(vereditos[c][caso])) > 1]
                 for c in CONDICOES}
    contagem = Counter(caso for lista in instaveis.values() for caso in lista)
    tokens = {c: {"entrada": media([r["uso"]["prompt_tokens"] for r in registros
                                    if r["condicao"] == c and r["status"] == "valido"]),
                  "saida": media([r["uso"]["completion_tokens"] for r in registros
                                  if r["condicao"] == c and r["status"] == "valido"])}
              for c in CONDICOES}
    return {
        "casos_por_mecanismo": dict(Counter(grupos.values())),
        "taxa_fp_por_mecanismo": fp_por_mecanismo,
        "fp_por_mecanismo": contagens,
        "instaveis": {c: {"total": len(v), "nao_vulneraveis":
                          sum(rotulos[caso] != VULN for caso in v)}
                      for c, v in instaveis.items()},
        "casos_instaveis_em_alguma_condicao": len(contagem),
        "casos_instaveis_em_2_ou_mais": sum(n >= 2 for n in contagem.values()),
        "tokens_medios": tokens,
    }


def teste_fingerprint(registros: list[dict], concs: dict) -> dict:
    """Nos pares (caso, condição) instáveis, o rótulo se associa ao system_fingerprint?
    Permutação dos fingerprints dentro de cada par; estatística: respostas
    VULNERAVEL no primeiro fingerprint."""
    respostas = {}
    for r in registros:
        if r["status"] == "valido" and concs[r["condicao"]][r["caso"]] not in (None, 1):
            respostas.setdefault((r["caso"], r["condicao"]), []).append(
                (r["veredito"], r.get("system_fingerprint")))
    if not respostas:
        return {"pares_instaveis": 0, "p": None}
    alvo = sorted({f for rs in respostas.values() for _, f in rs})[0]
    vereditos = [np.array([v == VULN for v, _ in rs]) for rs in respostas.values()]
    no_alvo = [np.array([f == alvo for _, f in rs]) for rs in respostas.values()]
    observado = sum(int((v & f).sum()) for v, f in zip(vereditos, no_alvo))
    rng = np.random.default_rng(SEMENTE_PERMUTACAO)
    nulos = np.array([sum(int((v & rng.permutation(f)).sum()) for v, f in zip(vereditos, no_alvo))
                      for _ in range(N_PERMUTACOES)])
    centro = nulos.mean()
    separados = sum(len({f for _, f in rs}) > 1 and
                    all(len({v for v, f in rs if f == g}) == 1 for g in {f for _, f in rs})
                    for rs in respostas.values())
    return {"pares_instaveis": len(respostas), "rotulo_separado_por_fingerprint": separados,
            "estatistica": observado, "esperado": float(centro),
            "p": float((np.abs(nulos - centro) >= abs(observado - centro)).mean())}


def complementar(rotulos: dict, casos: list[str], registros: list[dict], matrizes: dict,
                 acertos: dict, concs: dict, indices: np.ndarray) -> dict:
    """Números citados nas Seções 5.1, 5.2 e 5.5, definidos após a coleta."""
    cwe = {r["caso"]: r["cwe"] for r in registros}
    por_condicao = {}
    for c in CONDICOES:
        tp, fp, fn, tn = (int(v) for v in matrizes[c].sum(axis=0))
        sens, esp = razao(tp, tp + fn), razao(tn, tn + fp)
        den = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
        q = PREVALENCIA_TRIAGEM
        por_condicao[c] = {
            "especificidade": esp,
            "mcc": razao(tp * tn - fp * fn, den),
            "precisao_na_prevalencia": razao(q * sens, q * sens + (1 - q) * (1 - esp)),
            "fp_por_cwe": {w: int(sum(matrizes[c][i, 1] for i, caso in enumerate(casos)
                                      if cwe[caso] == w))
                           for w in sorted(set(cwe.values()))},
        }

    def f1_bootstrap(c):
        tp, fp, fn, _ = matrizes[c][indices].sum(axis=1).T.astype(float)
        return 2 * tp / (2 * tp + fp + fn)

    def f1(c):
        tp, fp, fn, _ = matrizes[c].sum(axis=0)
        return 2 * tp / (2 * tp + fp + fn)

    diferencas = {}
    for a, b in [*combinations(ESTRATEGIAS, 2), ("fluxo", "fluxo_skill")]:
        d = f1_bootstrap(b) - f1_bootstrap(a)
        diferencas[f"{b} - {a}"] = {"diferenca": float(f1(b) - f1(a)),
                                    "ic95": [float(np.percentile(d, 2.5)),
                                             float(np.percentile(d, 97.5))]}

    padroes = Counter("".join(str(int(acertos[c][i])) for c in ESTRATEGIAS)
                      for i in range(len(casos)))
    return {
        "prevalencia_triagem": PREVALENCIA_TRIAGEM,
        "por_condicao": por_condicao,
        "diferenca_f1_pareada": diferencas,
        "padroes_acerto": {"ordem": list(ESTRATEGIAS), "contagens": dict(sorted(padroes.items()))},
        "fingerprint_x_rotulo": teste_fingerprint(registros, concs),
    }


# ---------------------------------------------------------------- saída

def num(x, casas=3):
    return "--" if x is None else f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return "--" if x is None else f"{100 * x:.1f}\\%".replace(".", ",")


def com_ic(valor, ic):
    return f"{num(valor)} ({num(ic[0])}--{num(ic[1])})"


def valor_p(p):
    if p is None:
        return "--"
    if p < 0.001:
        return "$<$0,001"
    # Um p acima de ALFA não pode ser arredondado para o próprio ALFA.
    return num(p, 4) if round(p, 3) == ALFA and p > ALFA else num(p)


def tabelas_latex(res: dict) -> str:
    linhas = []
    for c in CONDICOES:
        d = res["condicoes"][c]
        ic = d["ic95"]
        linhas.append(" & ".join([
            NOMES[c], str(d["tp"]), str(d["fp"]), str(d["fn"]), str(d["tn"]),
            com_ic(d["precisao"], ic["precisao"]), com_ic(d["revocacao"], ic["revocacao"]),
            com_ic(d["f1"], ic["f1"]), pct(d["taxa_abstencao"]), num(d["cobertura"]),
            num(d["f1_efetivo"])]) + " \\\\")
    desempenho = "\n".join([
        "\\begin{table*}[t]",
        "\\caption{Desempenho por condição, sobre as execuções válidas (600 execuções por "
        "condição, menos as abstenções). Entre parênteses, IC de 95\\% por \\textit{bootstrap} "
        "reamostrando casos.}",
        "\\label{tab:desempenho}",
        "\\small",
        "\\begin{tabular}{lrrrrcccrcc}",
        "\\toprule",
        "Condição & TP & FP & FN & TN & Precisão & Revocação & F1 & Abstenção & Cobertura & F1 efetivo \\\\",
        "\\midrule", *linhas, "\\bottomrule", "\\end{tabular}", "\\end{table*}"])

    linhas = []
    for c in CONDICOES:
        e = res["condicoes"][c]["estabilidade"]
        linhas.append(" & ".join([
            NOMES[c],
            num(e["geral"]["media"]), num(e["vulneraveis"]["media"]),
            num(e["nao_vulneraveis"]["media"]),
            pct(e["geral"]["prop_unanimes"]), pct(e["vulneraveis"]["prop_unanimes"]),
            pct(e["nao_vulneraveis"]["prop_unanimes"])]) + " \\\\")
    estabilidade = "\n".join([
        "\\begin{table}[t]",
        "\\caption{Estabilidade por condição: concordância por pares média e proporção de "
        "casos unânimes, no total (T) e entre casos vulneráveis (V) e não vulneráveis (NV).}",
        "\\label{tab:estabilidade}",
        "\\small",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        " & \\multicolumn{3}{c}{Concordância média} & \\multicolumn{3}{c}{Casos unânimes} \\\\",
        "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
        "Condição & T & V & NV & T & V & NV \\\\",
        "\\midrule", *linhas, "\\bottomrule", "\\end{tabular}", "\\end{table}"])

    t = res["testes"]
    linhas = [f"Cochran Q (acerto, 3 estratégias) & -- & {num(t['cochran_acerto']['estatistica'], 2)} "
              f"& {valor_p(t['cochran_acerto']['p'])} & -- \\\\"]
    for par, x in t["mcnemar_acerto"].items():
        a, b = par.split(" x ")
        linhas.append(f"McNemar (acerto) & {NOMES[a]} $\\times$ {NOMES[b]} & "
                      f"{x['so_primeira_acerta']}/{x['so_segunda_acerta']} & {valor_p(x['p'])} & "
                      f"{valor_p(x['p_holm'])} \\\\")
    fr = t["friedman_concordancia"]
    linhas.append(f"Friedman (concordância, 3 estratégias) & -- & {num(fr['estatistica'], 2)} & "
                  f"{valor_p(fr['p'])} & -- \\\\")
    for par, x in t["wilcoxon_concordancia"].items():
        a, b = par.split(" x ")
        linhas.append(f"Wilcoxon (concordância) & {NOMES[a]} $\\times$ {NOMES[b]} & "
                      f"{num(x['estatistica'], 1)} & {valor_p(x['p'])} & {valor_p(x['p_holm'])} \\\\")
    x = t["skill_mcnemar_acerto"]
    linhas.append(f"McNemar (acerto) & {NOMES['fluxo']} $\\times$ {NOMES['fluxo_skill']} & "
                  f"{x['so_primeira_acerta']}/{x['so_segunda_acerta']} & {valor_p(x['p'])} & -- \\\\")
    x = t["skill_wilcoxon_concordancia"]
    linhas.append(f"Wilcoxon (concordância) & {NOMES['fluxo']} $\\times$ {NOMES['fluxo_skill']} & "
                  f"{num(x['estatistica'], 1)} & {valor_p(x['p'])} & -- \\\\")
    for c, x in t["mannwhitney_concordancia_por_rotulo"].items():
        linhas.append(f"Mann-Whitney (V $\\times$ NV) & {NOMES[c]} & {num(x['u'], 1)} & "
                      f"{valor_p(x['p'])} & {valor_p(x['p_holm'])} \\\\")
    testes = "\n".join([
        "\\begin{table*}[t]",
        "\\caption{Testes de hipótese. Acerto: voto majoritário por caso (empate conta como "
        "erro); no McNemar, a estatística indica quantos casos só a primeira/só a segunda "
        "condição acerta. Valores-$p$ ajustados por Holm dentro de cada família.}",
        "\\label{tab:testes}",
        "\\small",
        "\\begin{tabular}{llccc}",
        "\\toprule",
        "Teste & Comparação & Estatística & $p$ & $p$ (Holm) \\\\",
        "\\midrule", *linhas, "\\bottomrule", "\\end{tabular}", "\\end{table*}"])
    comp = res["complementar"]
    cwes = sorted(next(iter(comp["por_condicao"].values()))["fp_por_cwe"])
    linhas = []
    for c in CONDICOES:
        d = comp["por_condicao"][c]
        linhas.append(" & ".join([
            NOMES[c], num(d["especificidade"]), num(d["mcc"]), num(d["precisao_na_prevalencia"]),
            *(str(d["fp_por_cwe"][w]) for w in cwes)]) + " \\\\")
    prevalencia = f"{100 * comp['prevalencia_triagem']:.0f}\\%"
    complementares = "\n".join([
        "\\begin{table*}[t]",
        "\\caption{Medidas complementares, definidas após a coleta, por execução válida. "
        f"Precisão estimada para uma prevalência de {prevalencia} de casos vulneráveis, "
        "mantidas a revocação e a especificidade observadas.}",
        "\\label{tab:complementar}",
        "\\small",
        "\\begin{tabular}{lccc" + "r" * len(cwes) + "}",
        "\\toprule",
        " & & & & \\multicolumn{" + str(len(cwes)) + "}{c}{Falsos positivos por CWE} \\\\",
        "\\cmidrule(lr){5-" + str(4 + len(cwes)) + "}",
        f"Condição & Especificidade & MCC & Precisão ({prevalencia}) & "
        + " & ".join(f"CWE-{w}" for w in cwes) + " \\\\",
        "\\midrule", *linhas, "\\bottomrule", "\\end{tabular}", "\\end{table*}"])

    exp = res["exploratorio"]
    grupos = [("constante", "Constante"), ("condicao_fixa", "Condição fixa"), ("outro", "Demais")]
    linhas = []
    for c in CONDICOES:
        d = exp["fp_por_mecanismo"][c]
        linhas.append(" & ".join([NOMES[c], *(f"{d[g]['fp']}/{d[g]['execucoes']}"
                                              for g, _ in grupos)]) + " \\\\")
    mecanismos = "\n".join([
        "\\begin{table}[t]",
        "\\caption{Falsos positivos por execuções válidas nos casos não vulneráveis, "
        "agrupados após a coleta pelo mecanismo que neutraliza o fluxo (entre parênteses, "
        "o número de casos).}",
        "\\label{tab:mecanismos}",
        "\\small",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{tabular}{lccc}",
        "\\toprule",
        "Condição & " + " & ".join(f"{nome} ({exp['casos_por_mecanismo'][g]})"
                                    for g, nome in grupos) + " \\\\",
        "\\midrule", *linhas, "\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n\n".join([desempenho, estabilidade, testes, complementares, mecanismos]) + "\n"


def imprimir(res: dict) -> None:
    for c in CONDICOES:
        d = res["condicoes"][c]
        e = d["estabilidade"]
        print(f"\n== {c}")
        print(f"  TP={d['tp']} FP={d['fp']} FN={d['fn']} TN={d['tn']}  "
              f"P={num(d['precisao'])} R={num(d['revocacao'])} F1={num(d['f1'])} "
              f"IC_F1={[num(x) for x in d['ic95']['f1']]}")
        print(f"  abstenção={pct(d['taxa_abstencao'])} cobertura={num(d['cobertura'])} "
              f"F1ef={num(d['f1_efetivo'])} motivos={d['motivos_abstencao']}")
        print(f"  K={d['distribuicao_k']} voto={d['voto_majoritario']}")
        print(f"  concordância T/V/NV={num(e['geral']['media'])}/{num(e['vulneraveis']['media'])}/"
              f"{num(e['nao_vulneraveis']['media'])}  unânimes T/V/NV="
              f"{pct(e['geral']['prop_unanimes'])}/{pct(e['vulneraveis']['prop_unanimes'])}/"
              f"{pct(e['nao_vulneraveis']['prop_unanimes'])}")
        print(f"  por fingerprint={d['por_fingerprint']}")
    print("\n== testes")
    print(json.dumps(res["testes"], indent=2, ensure_ascii=False))
    print("\n== exploratório (pós-coleta)")
    print(json.dumps(res["exploratorio"], indent=2, ensure_ascii=False))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # console do Windows não é UTF-8 por padrão
    res = analisar()
    DIR_ANALISE.mkdir(exist_ok=True)
    (DIR_ANALISE / "resumo.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (DIR_ANALISE / "tabelas.tex").write_text(tabelas_latex(res), encoding="utf-8", newline="\n")
    imprimir(res)
    print(f"\nGravado em {DIR_ANALISE}")


if __name__ == "__main__":
    main()
