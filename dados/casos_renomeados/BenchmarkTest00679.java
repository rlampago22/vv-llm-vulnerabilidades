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

        org.owasp.benchmark.helpers.ThingInterface v3 =
                org.owasp.benchmark.helpers.ThingFactory.createThing();
        String v4 = v3.doSomething(v2);

        String v5 =
                "SELECT TOP 1 userid from USERS where USERNAME='foo' and PASSWORD='" + v4 + "'";
        try {
            java.util.Map<String, Object> v6 =
                    org.owasp.benchmark.helpers.DatabaseHelper.JDBCtemplate.queryForMap(v5);
            response.getWriter().println("Your results are: ");

            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v6.toString()));
        } catch (org.springframework.dao.EmptyResultDataAccessException v7) {
            response.getWriter()
                    .println(
                            "No results returned for query: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v5));
        } catch (org.springframework.dao.DataAccessException v7) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v7);
        }
    }
}
