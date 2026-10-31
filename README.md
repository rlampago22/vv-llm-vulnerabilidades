# Experimento: prompting, skill e estabilidade na detecção de vulnerabilidades

Código de coleta do artigo. Os parâmetros em `config.py` e os textos em `prompts.py`
espelham a Seção 4 do artigo: mudou um, mude o outro.

| Arquivo | Função |
|---|---|
| `config.py` | caminhos, sementes, CWEs, modelo e parâmetros de decodificação |
| `prompts.py` | system prompt, instruções das 4 condições e montagem das mensagens |
| `skill/revisao-seguranca-java/SKILL.md` | a skill da condição `fluxo_skill` |
| `anonimizacao.py` | remove comentários e identificadores dos casos |
| `preparar_amostra.py` | sorteio estratificado e gravação dos casos anonimizados |
| `coletar.py` | chamadas à API, log JSONL e parsing do veredito |
| `parsing.py` | regra de parsing pré-registrada (válido x abstenção) |
| `test_unidades.py` | testes do parsing e da anonimização |
| `analisar.py` | métricas, estabilidade, testes de hipótese e tabelas da Seção 5 |

## Organização do repositório

Este repositório é o pacote de replicação do artigo. O texto do artigo fica no
Overleaf; aqui ficam o protocolo, as entradas e as saídas do experimento.

```
experimento/
├── *.py, requirements.txt      protocolo: código de amostragem, coleta e parsing
├── skill/                      a skill avaliada (congelada antes da coleta)
├── dados/                      gerado por preparar_amostra.py e versionado
│   ├── amostra.csv             casos sorteados, rótulo, conjunto e sha256
│   └── casos/                  código anonimizado exatamente como enviado
├── resultados/                 gerado por coletar.py e versionado
│   ├── piloto.jsonl            não entra na análise
│   └── amostra.jsonl           uma linha por requisição
└── analise/                    gerado por analisar.py e versionado
    ├── resumo.json             todas as métricas e testes
    └── tabelas.tex             tabelas prontas para o artigo
```

Não são versionados: o clone do `BenchmarkJava/` (basta clonar de novo), o
`.venv/` e qualquer chave de API. Os casos em `dados/casos/` derivam do OWASP
Benchmark e seguem a licença daquele projeto.

Marcos do protocolo, cada um com commit e tag antes da etapa seguinte:

1. `protocolo-piloto`: código, prompts, skill e `dados/` prontos, antes do piloto;
2. `protocolo-final`: eventuais ajustes do piloto aplicados e skill congelada,
   antes da coleta da amostra;
3. `coleta-concluida`: `resultados/amostra.jsonl` completo.

## 1. Ambiente

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python test_unidades.py
```

## 2. Benchmark

```powershell
git clone https://github.com/OWASP-Benchmark/BenchmarkJava.git
```

O clone precisa ficar em `experimento\BenchmarkJava`. A amostra foi gerada a partir
do commit `f40c618c5a709afce350ef06ed2899c85cf586e9` (licença GPL-2.0); para
reproduzir exatamente, faça `git checkout` desse commit dentro do clone. O script lê
`expectedresults-1.2.csv` e os fontes em `src\main\java\org\owasp\benchmark\testcode`.

## 3. Amostra

```powershell
python preparar_amostra.py
```

Gera `dados\amostra.csv` com 128 casos: 120 da amostra (15 vulneráveis + 15 não
vulneráveis por CWE) e 8 do piloto (1 + 1 por CWE, sem sobreposição com a amostra).
O sorteio usa semente fixa, então rodar de novo produz o mesmo arquivo. O código
exatamente como será enviado ao modelo fica em `dados\casos\`.

Antes de seguir, abra alguns arquivos de `dados\casos\` e confira a anonimização.

## 4. Azure OpenAI

Implantação usada na coleta (assinatura Azure for Students, recurso Foundry):

| Item | Valor |
|---|---|
| Modelo e versão | `gpt-4.1-mini`, **2025-04-14** |
| Nome do deployment | `gpt41mini-vv` |
| Tipo | Padrão Global (*Global Standard*), 200K tokens por minuto |
| Atualização de versão | desativada (*opt out* das atualizações automáticas) |
| Filtro de conteúdo | DefaultV2 |
| Região do recurso | North Central US |
| Desativação da versão | 14/04/2027, 00h UTC |

O `gpt-4o-mini` 2024-07-18, planejado de início, já estava descontinuado e sem
cota para novas implantações nessa assinatura.

Depois, na sessão do PowerShell em que a coleta vai rodar, use o **Ponto de
extremidade do OpenAI do Azure** (não o do projeto):

```powershell
$env:AZURE_OPENAI_ENDPOINT   = "https://<seu-recurso>.openai.azure.com/"
$env:AZURE_OPENAI_API_KEY    = "sua-chave"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt41mini-vv"
```

Não grave a chave em nenhum arquivo do projeto. A versão da API (`AZURE_API_VERSION`)
fica fixa em `config.py`; o snapshot é conferido no campo `modelo_retornado` do log.

## 5. Piloto e coleta

```powershell
python coletar.py --conjunto piloto --dry-run   # mostra um prompt completo, sem chamar a API
python coletar.py --conjunto piloto             # 160 chamadas
python coletar.py --conjunto amostra            # 2.400 chamadas
```

O piloto serve para conferir o formato das respostas, a taxa de abstenção e o
tamanho das justificativas antes da coleta real. Os casos do piloto não entram na
análise.

A **skill deve estar congelada antes da coleta da amostra**: qualquer ajuste no
`SKILL.md` depois de ver as respostas da amostra invalida o contraste com o fluxo
de dados.

A coleta é retomável. Se cair no meio, ou se alguma requisição falhar por erro de
API depois das tentativas com backoff, rode o mesmo comando de novo: só o que
falta é enviado.

## 6. Análise

```powershell
python analisar.py
```

Não chama a API. Lê `resultados\amostra.jsonl` e grava `analise\resumo.json` e
`analise\tabelas.tex`. As regras de agregação estão no topo do script; a única
que o artigo não fixava antes da coleta é a do voto majoritário: empate (ou
nenhuma execução válida) conta como erro. Na coleta registrada não houve empate.
O bootstrap usa semente fixa (`SEMENTE_BOOTSTRAP`), então a saída é idêntica a
cada execução.

## Formato do log (`resultados\<conjunto>.jsonl`)

Uma linha por requisição, com o prompt completo, os parâmetros, a resposta bruta,
`finish_reason`, `system_fingerprint`, `request_id`, tokens e horários, além do
resultado do parsing:

- `status = "valido"`: `veredito` é `VULNERAVEL` ou `NAO_VULNERAVEL`;
- `status = "abstencao"`: resposta sem rótulo extraível, com o `motivo`
  (`truncado`, `json_invalido`, `sem_veredito`, `veredito_fora_do_dominio`...);
- `status = "filtro"`: bloqueio do filtro de conteúdo do Azure, no prompt
  (`filtro_prompt`) ou na resposta (`filtro_resposta`). **Não é abstenção**: é
  reportado à parte, por condição, e não é reenviado;
- `status = "erro_api"`: a requisição não obteve resposta. **Não é abstenção**:
  essas linhas são ignoradas na análise e a tarefa é reenviada na próxima execução.

Na análise, use para cada `id` a linha com `status` válido, abstenção ou filtro; as linhas
`erro_api` do mesmo `id` ficam no arquivo só como registro.

## Decisões que o código implementa

- **Sem `seed` na API.** Uma semente fixa tornaria as 5 repetições artificialmente
  iguais e inflaria a estabilidade.
- **Modo JSON sem esquema estrito** (`response_format = json_object`), para que a
  aderência ao formato continue mensurável.
- **Ordem aleatória** das requisições, com semente fixa (`SEMENTE_ORDEM`).
- **Skill no system prompt**: o corpo do `SKILL.md`, sem o frontmatter, é anexado
  ao system prompt comum; o user prompt é o mesmo da condição `fluxo`.

## Custo e tempo

A coleta registrada (2.400 chamadas com o `gpt-4.1-mini-2025-04-14`, 4 requisições
simultâneas) levou 14 min 35 s e consumiu 2,29 M tokens de entrada e 0,30 M de
saída, cerca de US$ 1,40 a preço de tabela. O snapshot tem desativação anunciada; faça a coleta bem antes dela
e guarde a pasta `resultados\`.
