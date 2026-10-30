"""Executa as requisições do experimento e grava uma linha JSONL por chamada.

Uso:
  python coletar.py --conjunto piloto --dry-run   # mostra o primeiro prompt, sem chamar a API
  python coletar.py --conjunto piloto             # 8 casos x 4 condições x 5 = 160 chamadas
  python coletar.py --conjunto amostra            # 120 casos x 4 condições x 5 = 2.400 chamadas

A coleta é retomável: ao rodar de novo, as requisições que já têm resposta
(válida, abstenção ou bloqueio do filtro de conteúdo) são puladas, e só as que
falharam por erro de API ou ainda não foram feitas são enviadas.

Variáveis de ambiente (Azure OpenAI): AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY
e AZURE_OPENAI_DEPLOYMENT.
"""

import argparse
import csv
import itertools
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from config import (ARQ_AMOSTRA, AZURE_API_VERSION, CWES, DIR_RESULTADOS, K_REPETICOES,
                    MAX_TOKENS_SAIDA, MODELO, SEMENTE_ORDEM, TEMPERATURA, TOP_P)
from parsing import interpretar
from prompts import CONDICOES, carregar_skill, montar_mensagens

# `model` é preenchido em main() com o nome do deployment do Azure.
PARAMETROS = {
    "temperature": TEMPERATURA,
    "top_p": TOP_P,
    "max_tokens": MAX_TOKENS_SAIDA,
    "response_format": {"type": "json_object"},
}
VARIAVEIS_AZURE = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT")
CONCLUIDOS = ("valido", "abstencao", "filtro")

_trava = threading.Lock()


def agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def carregar_casos(conjunto: str) -> list[dict]:
    if not ARQ_AMOSTRA.exists():
        sys.exit("dados/amostra.csv não existe. Rode antes: python preparar_amostra.py")
    with ARQ_AMOSTRA.open(encoding="utf-8") as f:
        casos = [c for c in csv.DictReader(f) if c["conjunto"] == conjunto]
    for caso in casos:
        caso["codigo"] = (ARQ_AMOSTRA.parent / caso["arquivo"]).read_text(encoding="utf-8")
    return casos


def montar_tarefas(casos: list[dict]) -> list[dict]:
    tarefas = [
        {"id": f"{caso['caso']}|{condicao}|{rep}", "caso": caso, "condicao": condicao,
         "repeticao": rep}
        for caso, condicao, rep in itertools.product(casos, CONDICOES,
                                                     range(1, K_REPETICOES + 1))
    ]
    # Ordem aleatória (semente fixa) para não confundir deriva do serviço com condição.
    random.Random(SEMENTE_ORDEM).shuffle(tarefas)
    for ordem, tarefa in enumerate(tarefas, start=1):
        tarefa["ordem"] = ordem
    return tarefas


def ids_concluidos(arquivo) -> set[str]:
    if not arquivo.exists():
        return set()
    concluidos = set()
    with arquivo.open(encoding="utf-8") as f:
        for linha in f:
            registro = json.loads(linha)
            if registro["status"] in CONCLUIDOS:
                concluidos.add(registro["id"])
    return concluidos


def executar(cliente, parametros: dict, tarefa: dict, corpo_skill: str) -> dict:
    caso = tarefa["caso"]
    cwe_num, cwe_nome = CWES[caso["categoria"]]
    mensagens = montar_mensagens(tarefa["condicao"], cwe_num, cwe_nome, caso["codigo"],
                                 corpo_skill)
    registro = {
        "id": tarefa["id"], "ordem": tarefa["ordem"], "caso": caso["caso"],
        "categoria": caso["categoria"], "cwe": cwe_num, "rotulo_real": caso["rotulo_real"],
        "sha256_codigo": caso["sha256"], "condicao": tarefa["condicao"],
        "repeticao": tarefa["repeticao"], "snapshot": MODELO,
        "api_version": AZURE_API_VERSION, "parametros": parametros, "mensagens": mensagens,
        "inicio": agora(),
    }
    t0 = time.perf_counter()
    try:
        resposta = cliente.chat.completions.create(messages=mensagens, **parametros)
    except Exception as erro:  # o cliente já fez backoff exponencial antes de desistir
        registro.update(fim=agora(), latencia_s=round(time.perf_counter() - t0, 3),
                        erro=f"{type(erro).__name__}: {erro}")
        # O Azure recusa com HTTP 400 e código content_filter um prompt barrado pelo
        # filtro de conteúdo: é categoria própria, não abstenção nem falha transitória.
        if getattr(erro, "code", None) == "content_filter":
            registro.update(status="filtro", veredito=None, motivo="filtro_prompt",
                            detalhe_erro=getattr(erro, "body", None))
        else:
            registro.update(status="erro_api")
        return registro

    escolha = resposta.choices[0]
    conteudo = escolha.message.content
    registro.update(
        fim=agora(),
        latencia_s=round(time.perf_counter() - t0, 3),
        request_id=getattr(resposta, "_request_id", None),
        modelo_retornado=resposta.model,
        system_fingerprint=resposta.system_fingerprint,
        finish_reason=escolha.finish_reason,
        resposta_bruta=conteudo,
        recusa=getattr(escolha.message, "refusal", None),
        uso=resposta.usage.model_dump() if resposta.usage else None,
        **interpretar(conteudo, escolha.finish_reason),
    )
    return registro


def gravar(arquivo, registro: dict) -> None:
    with _trava, arquivo.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--conjunto", choices=("piloto", "amostra"), required=True)
    parser.add_argument("--workers", type=int, default=4,
                        help="requisições simultâneas (padrão: 4)")
    parser.add_argument("--dry-run", action="store_true",
                        help="mostra o primeiro prompt e o total de tarefas, sem chamar a API")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # console do Windows não é UTF-8 por padrão

    corpo_skill = carregar_skill()
    tarefas = montar_tarefas(carregar_casos(args.conjunto))
    arquivo = DIR_RESULTADOS / f"{args.conjunto}.jsonl"
    concluidos = ids_concluidos(arquivo)
    pendentes = [t for t in tarefas if t["id"] not in concluidos]
    print(f"{len(tarefas)} tarefas, {len(concluidos)} já concluídas, {len(pendentes)} pendentes")

    if args.dry_run:
        exemplo = next(t for t in tarefas if t["condicao"] == "fluxo_skill")
        cwe_num, cwe_nome = CWES[exemplo["caso"]["categoria"]]
        for msg in montar_mensagens(exemplo["condicao"], cwe_num, cwe_nome,
                                    exemplo["caso"]["codigo"], corpo_skill):
            print(f"\n===== {msg['role']} =====\n{msg['content']}")
        return
    if not pendentes:
        return

    faltando = [v for v in VARIAVEIS_AZURE if not os.environ.get(v)]
    if faltando:
        sys.exit(f"Defina as variáveis de ambiente: {', '.join(faltando)} (ver README)")

    from openai import AzureOpenAI  # importado aqui para o --dry-run funcionar sem a chave
    cliente = AzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                          api_key=os.environ["AZURE_OPENAI_API_KEY"],
                          api_version=AZURE_API_VERSION, max_retries=8, timeout=120)
    parametros = {"model": os.environ["AZURE_OPENAI_DEPLOYMENT"], **PARAMETROS}

    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)
    status = {"valido": 0, "abstencao": 0, "filtro": 0, "erro_api": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futuros = [executor.submit(executar, cliente, parametros, t, corpo_skill)
                   for t in pendentes]
        for feitos, futuro in enumerate(as_completed(futuros), start=1):
            registro = futuro.result()
            gravar(arquivo, registro)
            status[registro["status"]] += 1
            if feitos % 50 == 0 or feitos == len(pendentes):
                print(f"{feitos}/{len(pendentes)} {status}", flush=True)

    if status["erro_api"]:
        print(f"{status['erro_api']} requisições falharam por erro de API; "
              "rode o mesmo comando de novo para reenviá-las.")


if __name__ == "__main__":
    main()
