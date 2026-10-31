"""Anonimização dos casos do OWASP Benchmark (Seção 4.3 do artigo).

Remove comentários com um analisador léxico simples, que respeita literais de
texto e de caractere, substitui os identificadores que revelam o caso e
neutraliza a palavra "safe" dentro de literais de texto.

O benchmark constrói muitos casos não vulneráveis trocando a entrada por
constantes como "safe", "moresafe" ou " SafeStuff"; o valor não altera a
vulnerabilidade, mas a palavra sinaliza o rótulo. A troca preserva o
comprimento e a caixa ("safe" -> "item"), para não mudar índices nem
comparações entre literais do mesmo arquivo.
"""

import re

NOME_CLASSE = "CasoAnalisado"
_RE_ID_CASO = re.compile(r"BenchmarkTest\d{5}")
_RE_WEBSERVLET = re.compile(r"@WebServlet\s*\([^)]*\)")
_RE_LITERAL = re.compile(r'"(?:[^"\\\n]|\\.)*"')
_RE_SAFE = re.compile(r"safe", re.IGNORECASE)
_NEUTRO = "item"


def _trocar_mantendo_caixa(m: re.Match) -> str:
    return "".join(n.upper() if o.isupper() else n for o, n in zip(m.group(), _NEUTRO))


def neutralizar_literais(codigo: str) -> str:
    return _RE_LITERAL.sub(lambda m: _RE_SAFE.sub(_trocar_mantendo_caixa, m.group()), codigo)


def remover_comentarios(fonte: str) -> str:
    saida = []
    i, n = 0, len(fonte)
    while i < n:
        c = fonte[i]
        prox = fonte[i + 1] if i + 1 < n else ""
        if c == "/" and prox == "/":
            fim = fonte.find("\n", i)
            i = n if fim == -1 else fim  # mantém a quebra de linha
        elif c == "/" and prox == "*":
            fim = fonte.find("*/", i + 2)
            fim = n if fim == -1 else fim + 2
            saida.append("\n" * fonte.count("\n", i, fim))
            i = fim
        elif fonte.startswith('"""', i):  # text block (Java 15+)
            fim = fonte.find('"""', i + 3)
            fim = n if fim == -1 else fim + 3
            saida.append(fonte[i:fim])
            i = fim
        elif c in "\"'":
            j = i + 1
            while j < n and fonte[j] != c and fonte[j] != "\n":
                j += 2 if fonte[j] == "\\" else 1
            j = min(j + 1, n)
            saida.append(fonte[i:j])
            i = j
        else:
            saida.append(c)
            i += 1
    return "".join(saida)


def _normalizar_linhas(fonte: str) -> str:
    linhas = [linha.rstrip() for linha in fonte.splitlines()]
    resultado = []
    for linha in linhas:
        if linha or (resultado and resultado[-1]):
            resultado.append(linha)
    return "\n".join(resultado).strip("\n") + "\n"


def anonimizar(fonte: str) -> str:
    codigo = remover_comentarios(fonte)
    codigo = _RE_ID_CASO.sub(NOME_CLASSE, codigo)
    codigo = _RE_WEBSERVLET.sub('@WebServlet(value = "/caso")', codigo)
    codigo = neutralizar_literais(codigo)
    return _normalizar_linhas(codigo)
