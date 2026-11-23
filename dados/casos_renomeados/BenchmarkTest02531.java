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

        String[] v1 = request.getParameterValues("CasoAnalisado");
        String v2;
        if (v1 != null && v1.length > 0) v2 = v1[0];
        else v2 = "";

        String v3 = metodo1(request, v2);

        String v4 = "SELECT * from USERS where USERNAME=? and PASSWORD='" + v3 + "'";

        try {
            java.sql.Connection v5 =
                    org.owasp.benchmark.helpers.DatabaseHelper.getSqlConnection();
            java.sql.PreparedStatement v6 =
                    v5.prepareStatement(v4, java.sql.Statement.RETURN_GENERATED_KEYS);
            v6.setString(1, "foo");
            v6.execute();
            org.owasp.benchmark.helpers.DatabaseHelper.printResults(v6, v4, response);
        } catch (java.sql.SQLException v7) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v7);
        }
    }

    private static String metodo1(HttpServletRequest request, String v2)
            throws ServletException, IOException {

        String v3;

        int num = 106;

        v3 = (7 * 42) - num > 200 ? "This should never happen" : v2;

        return v3;
    }
}
