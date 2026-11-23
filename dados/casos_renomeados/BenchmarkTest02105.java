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

        String v2 = metodo1(request, v1);

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

    private static String metodo1(HttpServletRequest request, String v1)
            throws ServletException, IOException {

        String v2 = "";
        if (v1 != null) {
            java.util.List<String> v4 = new java.util.ArrayList<String>();
            v4.add("item");
            v4.add(v1);
            v4.add("moreitem");

            v4.remove(0);

            v2 = v4.get(0);
        }

        return v2;
    }
}
