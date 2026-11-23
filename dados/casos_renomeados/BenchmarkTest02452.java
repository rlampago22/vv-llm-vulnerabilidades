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

        String v3 = metodo1(request, v2);

        String v4 = "SELECT * from USERS where USERNAME='foo' and PASSWORD='" + v3 + "'";

        try {
            java.util.List<java.util.Map<String, Object>> v5 =
                    org.owasp.benchmark.helpers.DatabaseHelper.JDBCtemplate.queryForList(v4);
            response.getWriter().println("Your results are: <br>");

            for (Object v6 : v5) {
                response.getWriter()
                        .println(
                                org.owasp.esapi.ESAPI.encoder().encodeForHTML(v6.toString())
                                        + "<br>");
            }
        } catch (org.springframework.dao.EmptyResultDataAccessException v7) {
            response.getWriter()
                    .println(
                            "No results returned for query: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v4));
        } catch (org.springframework.dao.DataAccessException v7) {
            if (org.owasp.benchmark.helpers.DatabaseHelper.hideSQLErrors) {
                response.getWriter().println("Error processing request.");
            } else throw new ServletException(v7);
        }
    }

    private static String metodo1(HttpServletRequest request, String v2)
            throws ServletException, IOException {

        String v8 = v2;
        StringBuilder v9 = new StringBuilder(v8);
        v9.append(" ItemStuff");
        v9.replace(
                v9.length() - "Chars".length(),
                v9.length(),
                "Chars");
        java.util.HashMap<String, Object> v10 = new java.util.HashMap<String, Object>();
        v10.put("key91263", v9.toString());
        String v11 = (String) v10.get("key91263");
        String v12 = v11.substring(0, v11.length() - 1);
        String v13 =
                new String(
                        org.apache.commons.codec.binary.Base64.decodeBase64(
                                org.apache.commons.codec.binary.Base64.encodeBase64(
                                        v12.getBytes())));
        String v14 = v13.split(" ")[0];
        org.owasp.benchmark.helpers.ThingInterface v15 =
                org.owasp.benchmark.helpers.ThingFactory.createThing();
        String v16 = "barbarians_at_the_gate";
        String v3 = v15.doSomething(v16);

        return v3;
    }
}
