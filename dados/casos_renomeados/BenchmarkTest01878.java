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
                new javax.servlet.http.Cookie("CasoAnalisado", "bar");
        v1.setMaxAge(60 * 3);
        v1.setSecure(true);
        v1.setHttpOnly(true);
        v1.setPath(request.getRequestURI());
        v1.setDomain(new java.net.URL(request.getRequestURL().toString()).getHost());
        response.addCookie(v1);
        javax.servlet.RequestDispatcher v2 =
                request.getRequestDispatcher("/sqli-04/CasoAnalisado.html");
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

        String v6 = metodo1(request, v4);

        String v7 = "SELECT * from USERS where USERNAME=? and PASSWORD='" + v6 + "'";

        try {
            java.sql.Connection v8 =
                    org.owasp.benchmark.helpers.DatabaseHelper.getSqlConnection();
            java.sql.PreparedStatement v9 =
                    v8.prepareStatement(v7, java.sql.Statement.RETURN_GENERATED_KEYS);
            v9.setString(1, "foo");
            v9.execute();
            org.owasp.benchmark.helpers.DatabaseHelper.printResults(v9, v7, response);
        } catch (java.sql.SQLException v10) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v10);
        }
    }

    private static String metodo1(HttpServletRequest request, String v4)
            throws ServletException, IOException {

        String v6;

        int num = 106;

        v6 = (7 * 18) + num > 200 ? "This_should_always_happen" : v4;

        return v6;
    }
}
