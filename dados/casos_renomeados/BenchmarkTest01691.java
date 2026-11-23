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

        String v5 =
                org.owasp.benchmark.helpers.Utils.getInsecureOSCommandString(
                        this.getClass().getClassLoader());

        String[] v6 = {v4};
        Runtime v7 = Runtime.getRuntime();

        try {
            Process v8 = v7.exec(v5, v6);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v8, response);
        } catch (IOException v9) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v9.getMessage()));
            return;
        }
    }

    private class Classe1 {

        public String metodo1(HttpServletRequest request, String v3)
                throws ServletException, IOException {

            String v4;
            String v10 = "ABC";
            char switchTarget = v10.charAt(2);

            switch (switchTarget) {
                case 'A':
                    v4 = v3;
                    break;
                case 'B':
                    v4 = "bobs_your_uncle";
                    break;
                case 'C':
                case 'D':
                    v4 = v3;
                    break;
                default:
                    v4 = "bobs_your_uncle";
                    break;
            }

            return v4;
        }
    }
}
