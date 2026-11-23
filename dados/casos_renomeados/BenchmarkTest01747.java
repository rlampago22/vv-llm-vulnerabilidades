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

        String v4 = "";
        if (System.getProperty("os.name").indexOf("Windows") != -1)
            if (System.getProperty("os.name").indexOf("Windows") != -1) v4 = "/";
            else v4 = "//";

        try {
            java.net.URI v5 =
                    new java.net.URI(
                            "file",
                            null,
                            v4
                                    + org.owasp.benchmark.helpers.Utils.TESTFILES_DIR
                                            .replace('\\', java.io.File.separatorChar)
                                            .replace(' ', '_')
                                    + v3,
                            null,
                            null);
            java.io.File v6 = new java.io.File(v5);
            response.getWriter()
                    .println(
                            "Access to file: '"
                                    + org.owasp
                                            .esapi
                                            .ESAPI
                                            .encoder()
                                            .encodeForHTML(v6.toString())
                                    + "' created.");
            if (v6.exists()) {
                response.getWriter().println(" And file already exists.");
            } else {
                response.getWriter().println(" But file doesn't exist yet.");
            }
        } catch (java.net.URISyntaxException v7) {
            throw new ServletException(v7);
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v2)
                throws ServletException, IOException {

            String v3;

            int num = 86;
            if ((7 * 42) - num > 200) v3 = "This_should_always_happen";
            else v3 = v2;

            return v3;
        }
    }
}
