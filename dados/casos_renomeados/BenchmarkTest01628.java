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

        String[] v1 = request.getParameterValues("CasoAnalisado");
        String v2;
        if (v1 != null && v1.length > 0) v2 = v1[0];
        else v2 = "";

        String v3 = new Classe1().doSomething(request, v2);

        String v4 = "SELECT * from USERS where USERNAME='foo' and PASSWORD='" + v3 + "'";

        try {
            java.sql.Statement v5 =
                    org.owasp.benchmark.helpers.DatabaseHelper.getSqlStatement();
            v5.execute(v4, new String[] {"username", "password"});
            org.owasp.benchmark.helpers.DatabaseHelper.printResults(v5, v4, response);
        } catch (java.sql.SQLException v6) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v6);
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v2)
                throws ServletException, IOException {

            String v3;
            String v7 = "ABC";
            char switchTarget = v7.charAt(1);

            switch (switchTarget) {
                case 'A':
                    v3 = v2;
                    break;
                case 'B':
                    v3 = "bob";
                    break;
                case 'C':
                case 'D':
                    v3 = v2;
                    break;
                default:
                    v3 = "bob's your uncle";
                    break;
            }

            return v3;
        }
    }
}
