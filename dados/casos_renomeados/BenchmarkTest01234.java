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

        java.io.File v3 =
                new java.io.File(org.owasp.benchmark.helpers.Utils.TESTFILES_DIR, v2);
        response.getWriter()
                .println(
                        "Access to file: '"
                                + org.owasp
                                        .esapi
                                        .ESAPI
                                        .encoder()
                                        .encodeForHTML(v3.toString())
                                + "' created.");
        if (v3.exists()) {
            response.getWriter().println(" And file already exists.");
        } else {
            response.getWriter().println(" But file doesn't exist yet.");
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v1)
                throws ServletException, IOException {

            org.owasp.benchmark.helpers.ThingInterface v4 =
                    org.owasp.benchmark.helpers.ThingFactory.createThing();
            String v2 = v4.doSomething(v1);

            return v2;
        }
    }
}
