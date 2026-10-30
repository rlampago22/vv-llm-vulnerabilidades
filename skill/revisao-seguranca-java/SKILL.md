---
name: revisao-seguranca-java
description: Revisão estática de segurança de código Java para servlets, cobrindo CWE-22 (Path Traversal), CWE-78 (OS Command Injection), CWE-79 (Cross-Site Scripting) e CWE-89 (SQL Injection), por rastreamento do fluxo de dados da entrada externa até a operação sensível. Use ao avaliar se um trecho de código Java contém uma dessas vulnerabilidades.
---

# Revisão de segurança de código Java

Esta skill orienta a decisão sobre a presença de **uma** CWE-alvo em um trecho de código Java. Avalie somente a CWE informada; outros problemas de segurança ou de qualidade do código não alteram a decisão.

## Procedimento

1. **Fontes.** Identifique os valores que vêm de fora da aplicação (lista em "Fontes de entrada").
2. **Propagação.** Acompanhe cada valor externo pelas atribuições, concatenações, chamadas de método, estruturas de dados e condicionais até o ponto em que é usado.
3. **Caminhos executáveis.** Considere apenas os caminhos que o código realmente pode executar. Quando uma condição tem resultado fixo, determinável pela leitura do próprio código, o ramo que nunca executa não leva o dado a lugar nenhum. Quando um valor externo é guardado em uma variável ou estrutura e depois substituído, verifique qual valor é de fato lido no ponto de uso.
4. **Operação sensível.** Verifique se o valor externo alcança uma operação sensível da CWE-alvo (listas por CWE abaixo).
5. **Sanitização.** Verifique se, no caminho entre a fonte e a operação sensível, existe uma sanitização **adequada à CWE-alvo**. Uma proteção feita para outra classe de vulnerabilidade não conta (por exemplo, codificar HTML não protege uma consulta SQL).
6. **Decisão.**
   - `VULNERAVEL`: existe um caminho executável em que um valor externo alcança a operação sensível da CWE-alvo sem sanitização adequada.
   - `NAO_VULNERAVEL`: não há operação sensível da CWE-alvo, o valor que a alcança não é externo, ou o caminho passa por sanitização adequada.

Quando o fluxo passa por um método cujo código não está visível, não presuma que ele sanitiza o valor: trate o resultado como ainda derivado da entrada, a menos que se trate de uma função de sanitização conhecida de biblioteca, citada nas listas abaixo.

## Fontes de entrada

Em servlets, são externos os valores obtidos de `HttpServletRequest`, entre eles:

- `getParameter`, `getParameterValues`, `getParameterMap`, `getParameterNames`;
- `getHeader`, `getHeaders`, `getHeaderNames`;
- `getCookies` (nome e valor de cada `Cookie`);
- `getQueryString`, `getPathInfo`, `getRequestURI`, `getInputStream`, `getReader`.

Continuam externos os valores derivados deles por concatenação, `StringBuilder`, `String.format`, `substring`, `split`, `replace`, `trim`, conversões de caixa, inclusão em listas, mapas ou vetores, e codificações reversíveis como Base64 ou URL (`URLDecoder.decode`). Codificar e decodificar um valor não o sanitiza.

## Conhecimento por CWE

### CWE-22: Path Traversal

- **Operações sensíveis:** construção de caminhos de arquivo usados para acesso, como `new File(...)`, `new FileInputStream(...)`, `new FileOutputStream(...)`, `new FileReader(...)`, `new FileWriter(...)`, `new RandomAccessFile(...)`, `java.nio.file.Paths.get(...)`, `Path.resolve(...)` e métodos de `java.nio.file.Files`.
- **Sanitização adequada:** obter o caminho canônico (`getCanonicalPath`, ou `toRealPath`/`normalize` em `Path`) e verificar que ele permanece dentro do diretório base permitido; aceitar apenas nomes de uma lista fechada (allowlist); rejeitar o valor quando contém `..` ou separadores de diretório.
- **Não é suficiente:** remover `../` uma única vez, validar apenas a extensão do arquivo, codificar o valor para HTML ou SQL.

### CWE-78: OS Command Injection

- **Operações sensíveis:** `Runtime.getRuntime().exec(...)` e `new ProcessBuilder(...)` seguido de `start()`, quando o comando, seus argumentos ou suas variáveis de ambiente são construídos com valores externos.
- **Sanitização adequada:** não usar valores externos na construção do comando; ou aceitar apenas valores de uma lista fechada (allowlist) definida no código.
- **Não é suficiente:** codificar o valor para HTML ou SQL, remover apenas alguns caracteres especiais, ou passar o valor como argumento separado a um interpretador de comandos (`sh -c`, `cmd /c`).

### CWE-79: Cross-Site Scripting

- **Operações sensíveis:** escrita do valor na resposta HTTP, como `response.getWriter().print/println/write/printf/format` e `response.getOutputStream().print/write`.
- **Sanitização adequada:** codificação de saída para o contexto HTML, por exemplo `ESAPI.encoder().encodeForHTML(...)`, `org.owasp.encoder.Encode.forHtml(...)`, `org.springframework.web.util.HtmlUtils.htmlEscape(...)` ou `StringEscapeUtils.escapeHtml4(...)`.
- **Não é suficiente:** codificação para SQL ou para linha de comando, ou validações que não neutralizam `<`, `>`, `"`, `'` e `&`.

### CWE-89: SQL Injection

- **Operações sensíveis:** execução de SQL construído com valores externos, como `Statement.execute/executeQuery/executeUpdate/addBatch`, `Connection.prepareStatement(...)` ou `prepareCall(...)` com SQL concatenado, e métodos de `JdbcTemplate` (`query`, `queryForObject`, `queryForList`, `queryForMap`, `update`, `execute`, `batchUpdate`) que recebem SQL concatenado.
- **Sanitização adequada:** consulta parametrizada, em que o texto SQL é constante, contém marcadores `?` e os valores externos são passados por `setString`, `setInt` e equivalentes, ou como argumentos de vinculação do `JdbcTemplate`.
- **Não é suficiente:** usar `PreparedStatement` com o valor externo concatenado no texto SQL, codificar o valor para HTML ou remover apenas aspas.

## Resposta

Mantenha o formato de resposta exigido pela instrução: no campo `justificativa`, descreva a origem do dado, a operação sensível e a sanitização encontrada (ou sua ausência), seguindo o procedimento acima; no campo `veredito`, use exclusivamente `VULNERAVEL` ou `NAO_VULNERAVEL`.
