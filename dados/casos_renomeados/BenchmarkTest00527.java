package org.owasp.benchmark.testcode;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet(v1 = "/caso")
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

        String v2 = "";
        boolean flag = true;
        java.util.Enumeration<String> v3 = request.getParameterNames();
        while (v3.hasMoreElements() && flag) {
            String v4 = (String) v3.nextElement();
            String[] v5 = request.getParameterValues(v4);
            if (v5 != null) {
                for (int i = 0; i < v5.length && flag; i++) {
                    String v1 = v5[i];
                    if (v1.equals("CasoAnalisado")) {
                        v2 = v4;
                        flag = false;
                    }
                }
            }
        }

        org.owasp.benchmark.helpers.ThingInterface v6 =
                org.owasp.benchmark.helpers.ThingFactory.createThing();
        String v7 = v6.doSomething(v2);

        java.io.File v8 = new java.io.File(v7, "/Test.txt");
        response.getWriter()
                .println(
                        "Access to file: '"
                                + org.owasp
                                        .esapi
                                        .ESAPI
                                        .encoder()
                                        .encodeForHTML(v8.toString())
                                + "' created.");
        if (v8.exists()) {
            response.getWriter().println(" And file already exists.");
        } else {
            response.getWriter().println(" But file doesn't exist yet.");
        }
    }
}
