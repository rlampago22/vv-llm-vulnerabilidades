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

        String v1 = request.getParameter("CasoAnalisado");
        if (v1 == null) v1 = "";

        String v2 = new Classe1().doSomething(request, v1);

        String v3 = "";
        String v4 = System.getProperty("os.name");
        if (v4.indexOf("Windows") != -1) {
            v3 = org.owasp.benchmark.helpers.Utils.getOSCommandString("echo");
        }

        Runtime v5 = Runtime.getRuntime();

        try {
            Process v6 = v5.exec(v3 + v2);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v6, response);
        } catch (IOException v7) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v7.getMessage()));
            return;
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v1)
                throws ServletException, IOException {

            String v2 = "";
            if (v1 != null) {
                java.util.List<String> v8 = new java.util.ArrayList<String>();
                v8.add("item");
                v8.add(v1);
                v8.add("moreitem");

                v8.remove(0);

                v2 = v8.get(0);
            }

            return v2;
        }
    }
}
