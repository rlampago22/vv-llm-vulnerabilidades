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
        String v2 = v1.getTheParameter("CasoAnalisado");
        if (v2 == null) v2 = "";

        String v3;

        int num = 86;
        if ((7 * 42) - num > 200) v3 = "This_should_always_happen";
        else v3 = v2;

        String v4 = null;
        java.io.FileOutputStream v5 = null;

        try {
            v4 = org.owasp.benchmark.helpers.Utils.TESTFILES_DIR + v3;

            v5 = new java.io.FileOutputStream(new java.io.File(v4), false);
            response.getWriter()
                    .println(
                            "Now ready to write to file: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v4));

        } catch (Exception v6) {
            System.out.println("Couldn't open FileOutputStream on file: '" + v4 + "'");

        } finally {
            if (v5 != null) {
                try {
                    v5.close();
                    v5 = null;
                } catch (Exception v6) {

                }
            }
        }
    }
}
