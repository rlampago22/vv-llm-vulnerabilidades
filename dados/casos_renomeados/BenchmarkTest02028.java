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
        java.util.Enumeration<String> v2 = request.getHeaders("CasoAnalisado");

        if (v2 != null && v2.hasMoreElements()) {
            v1 = v2.nextElement();
        }

        v1 = java.net.URLDecoder.decode(v1, "UTF-8");

        String v3 = metodo1(request, v1);

        java.io.File v4 =
                new java.io.File(org.owasp.benchmark.helpers.Utils.TESTFILES_DIR, v3);
        response.getWriter()
                .println(
                        "Access to file: '"
                                + org.owasp
                                        .esapi
                                        .ESAPI
                                        .encoder()
                                        .encodeForHTML(v4.toString())
                                + "' created.");
        if (v4.exists()) {
            response.getWriter().println(" And file already exists.");
        } else {
            response.getWriter().println(" But file doesn't exist yet.");
        }
    }

    private static String metodo1(HttpServletRequest request, String v1)
            throws ServletException, IOException {

        String v3;
        String v5 = "ABC";
        char switchTarget = v5.charAt(1);

        switch (switchTarget) {
            case 'A':
                v3 = v1;
                break;
            case 'B':
                v3 = "bob";
                break;
            case 'C':
            case 'D':
                v3 = v1;
                break;
            default:
                v3 = "bob's your uncle";
                break;
        }

        return v3;
    }
}
