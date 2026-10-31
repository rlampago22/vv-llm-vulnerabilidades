"""Testes da regra de parsing e da anonimização.

Rodar com: python test_unidades.py   (ou: python -m pytest test_unidades.py)
"""

from anonimizacao import anonimizar, neutralizar_literais, remover_comentarios
from parsing import interpretar

JAVA = '''/**
 * OWASP Benchmark Project v1.2
 * @created 2015
 */
package org.owasp.benchmark.testcode;

@WebServlet(value = "/sqli-00/BenchmarkTest00008")
public class BenchmarkTest00008 extends HttpServlet {
    // comentário de linha
    String url = "http://exemplo.com/a"; /* bloco */ String b = "/* não é comentário */";
    char barra = '/'; char aspas = '"';
    String param = request.getHeader("BenchmarkTest00008"); // fim
}
'''


def test_remove_comentarios_preservando_literais():
    saida = remover_comentarios(JAVA)
    assert "OWASP Benchmark Project" not in saida
    assert "comentário de linha" not in saida
    assert "bloco" not in saida
    assert '"http://exemplo.com/a"' in saida
    assert '"/* não é comentário */"' in saida
    assert "char barra = '/';" in saida
    assert "char aspas = '\"';" in saida


def test_anonimiza_identificadores():
    saida = anonimizar(JAVA)
    assert "BenchmarkTest" not in saida
    assert "public class CasoAnalisado extends HttpServlet" in saida
    assert '@WebServlet(value = "/caso")' in saida
    assert 'request.getHeader("CasoAnalisado")' in saida
    assert saida.startswith("package org.owasp.benchmark.testcode;")
    assert "\n\n\n" not in saida


def test_neutraliza_safe_so_em_literais():
    codigo = ('valuesList.add("safe"); String bar = "safe!"; sb.append(" SafeStuff");\n'
              'x = "moresafe"; y = "_SafeDonna"; boolean safeMode = true;')
    saida = neutralizar_literais(codigo)
    assert 'valuesList.add("item")' in saida
    assert '"item!"' in saida and '" ItemStuff"' in saida
    assert '"moreitem"' in saida and '"_ItemDonna"' in saida
    assert "boolean safeMode" in saida  # fora de literal, não muda
    assert len(saida) == len(codigo)


def test_parsing_valido():
    r = interpretar('{"justificativa": "a", "veredito": "VULNERAVEL"}', "stop")
    assert r["status"] == "valido" and r["veredito"] == "VULNERAVEL"
    assert r["tam_justificativa"] == 1
    r = interpretar('{"justificativa": "", "veredito": " NAO_VULNERAVEL "}', "stop")
    assert r["veredito"] == "NAO_VULNERAVEL"


def test_parsing_abstencoes():
    casos = {
        ('{"veredito": "VULNERAVEL"', "length"): "truncado",
        (None, "stop"): "vazio",
        ('```json\n{"veredito": "VULNERAVEL"}\n```', "stop"): "json_invalido",
        ('["VULNERAVEL"]', "stop"): "json_nao_objeto",
        ('{"justificativa": "x"}', "stop"): "sem_veredito",
        ('{"veredito": "vulneravel"}', "stop"): "veredito_fora_do_dominio",
        ('{"veredito": "VULNERAVEL ou NAO_VULNERAVEL"}', "stop"): "veredito_fora_do_dominio",
        ('{"veredito": true}', "stop"): "veredito_fora_do_dominio",
    }
    for (conteudo, fim), motivo in casos.items():
        r = interpretar(conteudo, fim)
        assert r["status"] == "abstencao" and r["veredito"] is None, conteudo
        assert r["motivo"] == motivo, (conteudo, r["motivo"])


def test_parsing_filtro_separado_da_abstencao():
    r = interpretar('{"veredito": "VULNERAVEL"}', "content_filter")
    assert r["status"] == "filtro" and r["veredito"] is None
    assert r["motivo"] == "filtro_resposta"


if __name__ == "__main__":
    for nome, funcao in list(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print("ok", nome)
