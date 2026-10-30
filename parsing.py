"""Regra de parsing pré-registrada (Seção 2.4 e 4.4 do artigo).

Uma resposta só vira rótulo quando é um objeto JSON cujo campo `veredito` é
exatamente um dos dois valores permitidos (ignorando apenas espaços nas
bordas; maiúsculas e minúsculas importam). Uma resposta cortada pelo filtro de
conteúdo do Azure é registrada como `filtro`, categoria separada da abstenção
(Seção 4.6). Qualquer outra coisa é abstenção, com o motivo registrado; nenhum
rótulo é inferido por heurística.
"""

import json

ROTULOS = ("VULNERAVEL", "NAO_VULNERAVEL")


def interpretar(conteudo: str | None, finish_reason: str | None) -> dict:
    def abstencao(motivo: str) -> dict:
        return {"status": "abstencao", "veredito": None, "motivo": motivo,
                "tam_justificativa": None}

    if finish_reason == "content_filter":
        return {"status": "filtro", "veredito": None, "motivo": "filtro_resposta",
                "tam_justificativa": None}
    if finish_reason == "length":
        return abstencao("truncado")
    if finish_reason not in (None, "stop"):
        return abstencao(f"finish_reason:{finish_reason}")
    if not conteudo or not conteudo.strip():
        return abstencao("vazio")
    try:
        obj = json.loads(conteudo)
    except json.JSONDecodeError:
        return abstencao("json_invalido")
    if not isinstance(obj, dict):
        return abstencao("json_nao_objeto")
    if "veredito" not in obj:
        return abstencao("sem_veredito")
    veredito = obj["veredito"]
    if not isinstance(veredito, str) or veredito.strip() not in ROTULOS:
        return abstencao("veredito_fora_do_dominio")

    justificativa = obj.get("justificativa")
    return {
        "status": "valido",
        "veredito": veredito.strip(),
        "motivo": None,
        "tam_justificativa": len(justificativa) if isinstance(justificativa, str) else None,
    }
