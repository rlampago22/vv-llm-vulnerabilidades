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

        String v1 = "";
        java.util.Enumeration<String> v2 = request.getHeaders("Referer");

        if (v2 != null && v2.hasMoreElements()) {
            v1 = v2.nextElement();
        }

        v1 = java.net.URLDecoder.decode(v1, "UTF-8");

        String v3 = new Classe1().doSomething(request, v1);

        response.setHeader("X-XSS-Protection", "0");
        Object[] v4 = {"a", v3};
        response.getWriter().printf(java.util.Locale.US, "Formatted like: %1$s and %2$s.", v4);
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v1)
                throws ServletException, IOException {

            String v3 = org.owasp.esapi.ESAPI.encoder().encodeForHTML(v1);

            return v3;
        }
    }
}
