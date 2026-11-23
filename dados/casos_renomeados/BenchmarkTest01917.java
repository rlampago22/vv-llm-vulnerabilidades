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
        if (request.getHeader("Referer") != null) {
            v1 = request.getHeader("Referer");
        }

        v1 = java.net.URLDecoder.decode(v1, "UTF-8");

        String v2 = metodo1(request, v1);

        response.setHeader("X-XSS-Protection", "0");
        response.getWriter().print(v2);
    }

    private static String metodo1(HttpServletRequest request, String v1)
            throws ServletException, IOException {

        String v2 = org.owasp.esapi.ESAPI.encoder().encodeForHTML(v1);

        return v2;
    }
}
