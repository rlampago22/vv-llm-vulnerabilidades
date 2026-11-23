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

        java.io.File v5 =
                new java.io.File(org.owasp.benchmark.helpers.Utils.TESTFILES_DIR, v4);
        response.getWriter()
                .println(
                        "Access to file: '"
                                + org.owasp
                                        .esapi
                                        .ESAPI
                                        .encoder()
                                        .encodeForHTML(v5.toString())
                                + "' created.");
        if (v5.exists()) {
            response.getWriter().println(" And file already exists.");
        } else {
            response.getWriter().println(" But file doesn't exist yet.");
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v3)
                throws ServletException, IOException {

            org.owasp.benchmark.helpers.ThingInterface v6 =
                    org.owasp.benchmark.helpers.ThingFactory.createThing();
            String v4 = v6.doSomething(v3);

            return v4;
        }
    }
}
