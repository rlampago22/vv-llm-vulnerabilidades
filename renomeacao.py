"""Renomeação de identificadores para o teste de contaminação (Seção 4.6 do artigo).

Troca por nomes neutros (v1, v2, ...; metodo1, ...; Classe1, ...) todos os
identificadores DECLARADOS no próprio caso: variáveis locais, parâmetros,
campos, métodos e classes internas. Ficam intactos:
  - literais de texto e de caractere;
  - membros acessados com ponto (métodos e campos de bibliotecas e de classes
    auxiliares do benchmark, que não foram enviadas ao modelo);
  - a classe do caso, os métodos sobrescritos (doGet, doPost e os marcados com
    @Override), serialVersionUID e os parâmetros request/response da API de servlets.

Se a classificação depender de o modelo ter memorizado os casos do benchmark,
a troca dos nomes característicos (param, bar, doSomething, ...) deve reduzir
o acerto. A estrutura do código e as chamadas de API são preservadas.
"""

import re

PALAVRAS_RESERVADAS = set("""
abstract assert boolean break byte case catch char class const continue default do double
else enum extends final finally float for goto if implements import instanceof int interface
long native new package private protected public return short static strictfp super switch
synchronized this throw throws transient try void volatile while var true false null record
yield sealed permits
""".split())
PRESERVAR = {"CasoAnalisado", "doGet", "doPost", "serialVersionUID", "request", "response",
             "main", "args"}

_RE_LITERAL = re.compile(r'"""[\s\S]*?"""|"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'')
_RE_IDENT = re.compile(r"[A-Za-z_$][\w$]*")
# Tipo (possivelmente qualificado, genérico e/ou array) seguido do nome declarado.
_RE_DECL_VAR = re.compile(
    r"(?<![\w.$])([A-Za-z_][\w.$]*)\s*(?:<(?:[^<>;(){}=]|<[^<>;(){}=]*>)*>)?\s*(?:\[\s*\]\s*)*"
    r"\s+([A-Za-z_$][\w$]*)\s*(?=[=;,):])")
_RE_DECL_METODO = re.compile(
    r"((?:@Override\s+)?)(?:(?:public|private|protected|static|final|synchronized|abstract)\s+)+"
    r"[\w.$<>\[\], ]+?\s+([A-Za-z_$][\w$]*)\s*\(")
_RE_DECL_CLASSE = re.compile(r"\b(?:class|interface|enum)\s+([A-Za-z_$][\w$]*)")


def _mascarar_literais(codigo: str) -> str:
    """Troca o conteúdo dos literais por espaços, preservando as posições."""
    return _RE_LITERAL.sub(lambda m: " " * len(m.group()), codigo)


def declarados(codigo: str) -> dict[str, str]:
    """Nomes declarados no caso, com o tipo de declaração (var, metodo, classe)."""
    mascarado = _mascarar_literais(codigo)
    nomes: dict[str, str] = {}
    for m in _RE_DECL_CLASSE.finditer(mascarado):
        nomes.setdefault(m.group(1), "classe")
    for m in _RE_DECL_METODO.finditer(mascarado):
        if not m.group(1):  # métodos com @Override mantêm o nome da interface
            nomes.setdefault(m.group(2), "metodo")
    for m in _RE_DECL_VAR.finditer(mascarado):
        tipo, nome = m.group(1), m.group(2)
        if tipo.split(".")[0] in PALAVRAS_RESERVADAS:
            continue
        nomes.setdefault(nome, "var")
    return {n: k for n, k in nomes.items()
            if n not in PALAVRAS_RESERVADAS and n not in PRESERVAR}


def renomear(codigo: str) -> tuple[str, dict[str, str]]:
    """Devolve o código renomeado e o mapa nome original -> nome novo."""
    nomes = declarados(codigo)
    mascarado = _mascarar_literais(codigo)
    existentes = set(_RE_IDENT.findall(mascarado))
    prefixo = {"var": "v", "metodo": "metodo", "classe": "Classe"}
    contador = {"var": 0, "metodo": 0, "classe": 0}
    mapa: dict[str, str] = {}
    # Ordem de primeira ocorrência no código, para o mapa ser determinístico.
    for m in _RE_IDENT.finditer(mascarado):
        nome = m.group()
        if nome in nomes and nome not in mapa:
            tipo = nomes[nome]
            while True:
                contador[tipo] += 1
                novo = f"{prefixo[tipo]}{contador[tipo]}"
                if novo not in existentes:
                    break
            mapa[nome] = novo

    partes, ultimo = [], 0
    for m in _RE_IDENT.finditer(mascarado):
        nome = m.group()
        if nome not in mapa:
            continue
        antes = mascarado[:m.start()].rstrip()
        if antes.endswith(".") or antes.endswith("::"):
            continue  # membro de outro objeto ou classe
        partes.append(codigo[ultimo:m.start()])
        partes.append(mapa[nome])
        ultimo = m.end()
    partes.append(codigo[ultimo:])
    return "".join(partes), mapa
