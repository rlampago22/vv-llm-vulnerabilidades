"""Textos dos prompts, idênticos aos da Seção 4.2 do artigo."""

from config import ARQ_SKILL

SYSTEM_PROMPT = (
    "Você é um especialista em segurança de software realizando inspeção estática "
    "de código Java. Avalie se o código contém a vulnerabilidade da categoria CWE "
    "informada e responda exclusivamente com um objeto JSON válido no formato "
    '{"justificativa": "...", "veredito": "VULNERAVEL" ou "NAO_VULNERAVEL"}.'
)

_INSTRUCAO_FLUXO = (
    "Analise o código Java abaixo quanto à presença da CWE indicada. No campo "
    "justificativa, identifique em sequência: (1) a origem dos dados de entrada, "
    "(2) a operação sensível relacionada à CWE e (3) a presença ou ausência de "
    "sanitização adequada no fluxo entre elas. Em seguida, informe a decisão final "
    "no campo veredito."
)

INSTRUCOES = {
    "zero_shot": (
        "Analise o código Java abaixo quanto à presença da CWE indicada. Classifique "
        'diretamente o caso mantendo o campo justificativa vazio ("") e informando a '
        "decisão final no campo veredito."
    ),
    "cot": (
        "Analise o código Java abaixo quanto à presença da CWE indicada. Pense passo a "
        "passo, descrevendo as etapas do seu raciocínio no campo justificativa antes de "
        "informar a decisão final no campo veredito."
    ),
    "fluxo": _INSTRUCAO_FLUXO,
    # Mesma instrução da estratégia de fluxo de dados: só o system prompt muda.
    "fluxo_skill": _INSTRUCAO_FLUXO,
}

CONDICOES = tuple(INSTRUCOES)


def carregar_skill() -> str:
    """Corpo do SKILL.md sem o frontmatter YAML, que é o que entra no contexto
    quando um agente ativa a skill."""
    texto = ARQ_SKILL.read_text(encoding="utf-8")
    if texto.startswith("---"):
        _, _, texto = texto[3:].partition("\n---")
    return texto.strip()


def montar_mensagens(condicao: str, cwe_num: int, cwe_nome: str, codigo: str,
                     corpo_skill: str) -> list[dict]:
    system = SYSTEM_PROMPT
    if condicao == "fluxo_skill":
        system = f"{SYSTEM_PROMPT}\n\n{corpo_skill}"
    user = (
        f"CWE-alvo: CWE-{cwe_num} ({cwe_nome})\n\n"
        f"{INSTRUCOES[condicao]}\n\n"
        f"```java\n{codigo}\n```"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
