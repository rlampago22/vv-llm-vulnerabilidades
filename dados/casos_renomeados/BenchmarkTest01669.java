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

        response.setHeader("X-XSS-Protection", "0");
        response.getWriter().println(v4);
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v3)
                throws ServletException, IOException {

            String v4 = org.owasp.esapi.ESAPI.encoder().encodeForHTML(v3);

            return v4;
        }
    }
}
