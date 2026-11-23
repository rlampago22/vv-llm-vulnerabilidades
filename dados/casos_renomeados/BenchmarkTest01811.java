package org.owasp.benchmark.testcode;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet(value = "/caso")
public class CasoAnalisado extends HttpServlet {

    private static final long serialVersionUID = 1L;

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doPost(request, response);
    }

    @Override
    public void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");

        org.owasp.benchmark.helpers.SeparateClassRequest v1 =
                new org.owasp.benchmark.helpers.SeparateClassRequest(request);
        String v2 = v1.getTheValue("CasoAnalisado");

        String v3 = new Classe1().doSomething(request, v2);

        String v4 =
                "SELECT TOP 1 userid from USERS where USERNAME='foo' and PASSWORD='" + v3 + "'";
        try {
            java.util.Map<String, Object> v5 =
                    org.owasp.benchmark.helpers.DatabaseHelper.JDBCtemplate.queryForMap(v4);
            response.getWriter().println("Your results are: ");

            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v5.toString()));
        } catch (org.springframework.dao.EmptyResultDataAccessException v6) {
            response.getWriter()
                    .println(
                            "No results returned for query: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v4));
        } catch (org.springframework.dao.DataAccessException v6) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v6);
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v2)
                throws ServletException, IOException {

            String v3 = "item!";
            java.util.HashMap<String, Object> v7 = new java.util.HashMap<String, Object>();
            v7.put("keyA-31047", "a_Value");
            v7.put("keyB-31047", v2);
            v7.put("keyC", "another_Value");
            v3 = (String) v7.get("keyB-31047");
            v3 = (String) v7.get("keyA-31047");

            return v3;
        }
    }
}
