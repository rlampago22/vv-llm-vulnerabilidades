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
        response.setContentType("text/html;charset=UTF-8");
        javax.servlet.http.Cookie v1 =
                new javax.servlet.http.Cookie("CasoAnalisado", "FOO%3Decho+Injection");
        v1.setMaxAge(60 * 3);
        v1.setSecure(true);
        v1.setHttpOnly(true);
        v1.setPath(request.getRequestURI());
        v1.setDomain(new java.net.URL(request.getRequestURL().toString()).getHost());
        response.addCookie(v1);
        javax.servlet.RequestDispatcher v2 =
                request.getRequestDispatcher("/cmdi-00/CasoAnalisado.html");
        v2.include(request, response);
    }

    @Override
    public void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");

        javax.servlet.http.Cookie[] v3 = request.getCookies();

        String v4 = "noCookieValueSupplied";
        if (v3 != null) {
            for (javax.servlet.http.Cookie v5 : v3) {
                if (v5.getName().equals("CasoAnalisado")) {
                    v4 = java.net.URLDecoder.decode(v5.getValue(), "UTF-8");
                    break;
                }
            }
        }

        String v6;
        String v7 = "ABC";
        char switchTarget = v7.charAt(2);

        switch (switchTarget) {
            case 'A':
                v6 = v4;
                break;
            case 'B':
                v6 = "bobs_your_uncle";
                break;
            case 'C':
            case 'D':
                v6 = v4;
                break;
            default:
                v6 = "bobs_your_uncle";
                break;
        }

        String v8 =
                org.owasp.benchmark.helpers.Utils.getInsecureOSCommandString(
                        this.getClass().getClassLoader());
        String[] args = {v8};
        String[] v9 = {v6};

        Runtime v10 = Runtime.getRuntime();

        try {
            Process v11 = v10.exec(args, v9);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v11, response);
        } catch (IOException v12) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v12.getMessage()));
            return;
        }
    }
}
