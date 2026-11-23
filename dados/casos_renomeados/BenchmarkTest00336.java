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

        String v3;

        int num = 86;
        if ((7 * 42) - num > 200) v3 = "This_should_always_happen";
        else v3 = v1;

        String v4 = "SELECT userid from USERS where USERNAME='foo' and PASSWORD='" + v3 + "'";
        try {

            Long v5 =
                    org.owasp.benchmark.helpers.DatabaseHelper.JDBCtemplate.queryForObject(
                            v4, Long.class);
            response.getWriter().println("Your results are: " + String.valueOf(v5));
        } catch (org.springframework.dao.EmptyResultDataAccessException v6) {
            response.getWriter()
                    .println(
                            "No results returned for query: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v4));
        } catch (org.springframework.dao.DataAccessException v6) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v6);
        }
    }
}
