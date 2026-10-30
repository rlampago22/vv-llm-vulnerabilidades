"""Parâmetros fixos do experimento. Espelham a Seção 4 (Metodologia) do artigo:
qualquer mudança aqui precisa ser refletida no texto, e vice-versa."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# OWASP Benchmark for Java v1.2, clonado em experimento/BenchmarkJava (ver README).
DIR_BENCHMARK = RAIZ / "BenchmarkJava"
ARQ_GABARITO = DIR_BENCHMARK / "expectedresults-1.2.csv"
DIR_FONTES = DIR_BENCHMARK / "src" / "main" / "java" / "org" / "owasp" / "benchmark" / "testcode"

DIR_DADOS = RAIZ / "dados"
DIR_CASOS = DIR_DADOS / "casos"
ARQ_AMOSTRA = DIR_DADOS / "amostra.csv"
DIR_RESULTADOS = RAIZ / "resultados"
ARQ_SKILL = RAIZ / "skill" / "revisao-seguranca-java" / "SKILL.md"

# Sementes fixas: sorteio dos casos e ordem de envio das requisições.
SEMENTE_AMOSTRA = 20261027
SEMENTE_ORDEM = 20261028

# 15 vulneráveis + 15 não vulneráveis por CWE na amostra; 1 + 1 por CWE no piloto,
# sorteados do mesmo conjunto, mas disjuntos da amostra.
CASOS_POR_ROTULO = 15
PILOTO_POR_ROTULO = 1

# categoria no expectedresults -> (número da CWE, nome usado no prompt)
CWES = {
    "pathtraver": (22, "Path Traversal"),
    "cmdi": (78, "OS Command Injection"),
    "xss": (79, "Cross-Site Scripting"),
    "sqli": (89, "SQL Injection"),
}

# Snapshot implantado no Azure OpenAI (deployment com atualização automática de
# versão desativada). Na API do Azure, o campo `model` recebe o nome do deployment,
# lido de AZURE_OPENAI_DEPLOYMENT; o snapshot fica registrado aqui e é conferido
# contra o `model` devolvido em cada resposta.
MODELO = "gpt-4.1-mini-2025-04-14"
AZURE_API_VERSION = "2024-10-21"
TEMPERATURA = 0.2
TOP_P = 0.9
MAX_TOKENS_SAIDA = 1024
K_REPETICOES = 5

# Nenhum `seed` é enviado à API: uma semente fixa tornaria as K repetições
# artificialmente iguais e inflaria a estabilidade medida.
