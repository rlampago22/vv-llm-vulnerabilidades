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
                org.owasp.benchmark.helpers.Utils.getInsecureOSCommandString(
                        this.getClass().getClassLoader());
        String[] args = {v4};
        String[] v5 = {v3};

        Runtime v6 = Runtime.getRuntime();

        try {
            Process v7 = v6.exec(args, v5);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v7, response);
        } catch (IOException v8) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v8.getMessage()));
            return;
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v2)
                throws ServletException, IOException {

            String v3;
            String v9 = "ABC";
            char switchTarget = v9.charAt(1);

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
