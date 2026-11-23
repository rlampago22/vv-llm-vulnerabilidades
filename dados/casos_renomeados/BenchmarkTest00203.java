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
        if (request.getHeader("CasoAnalisado") != null) {
            v1 = request.getHeader("CasoAnalisado");
        }

        v1 = java.net.URLDecoder.decode(v1, "UTF-8");

        String v2;

        int num = 106;

        v2 = (7 * 42) - num > 200 ? "This should never happen" : v1;

        String v3 = "INSERT INTO users (username, password) VALUES ('foo','" + v2 + "')";

        try {
            java.sql.Statement v4 =
                    org.owasp.benchmark.helpers.DatabaseHelper.getSqlStatement();
            int count = v4.executeUpdate(v3, new String[] {"USERNAME", "PASSWORD"});
            org.owasp.benchmark.helpers.DatabaseHelper.outputUpdateComplete(v3, response);
        } catch (java.sql.SQLException v5) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v5);
        }
    }
}
