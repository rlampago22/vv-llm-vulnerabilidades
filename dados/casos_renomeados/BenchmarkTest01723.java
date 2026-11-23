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

        String v1 = request.getQueryString();
        String v2 = "CasoAnalisado" + "=";
        int paramLoc = -1;
        if (v1 != null) paramLoc = v1.indexOf(v2);
        if (paramLoc == -1) {
            response.getWriter()
                    .println(
                            "getQueryString() couldn't find expected parameter '"
                                    + "CasoAnalisado"
                                    + "' in query string.");
            return;
        }

        String v3 =
                v1.substring(
                        paramLoc
                                + v2
                                        .length());

        int ampersandLoc = v1.indexOf("&", paramLoc);
        if (ampersandLoc != -1) {
            v3 = v1.substring(paramLoc + v2.length(), ampersandLoc);
        }
        v3 = java.net.URLDecoder.decode(v3, "UTF-8");

        String v4 = new Classe1().doSomething(request, v3);

        String v5 = "SELECT userid from USERS where USERNAME='foo' and PASSWORD='" + v4 + "'";

        try {

            Integer v6 =
                    org.owasp.benchmark.helpers.DatabaseHelper.JDBCtemplate.queryForObject(
                            v5, Integer.class);
            response.getWriter().println("Your results are: " + v6);

        } catch (org.springframework.dao.EmptyResultDataAccessException v7) {
            response.getWriter()
                    .println(
                            "No results returned for query: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v5));
        } catch (org.springframework.dao.DataAccessException v7) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v7);
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v3)
                throws ServletException, IOException {

            String v4;

            int num = 106;

            v4 = (7 * 42) - num > 200 ? "This should never happen" : v3;

            return v4;
        }
    }
}
