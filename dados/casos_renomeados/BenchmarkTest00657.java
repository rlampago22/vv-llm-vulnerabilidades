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

        String v3 = "item!";
        java.util.HashMap<String, Object> v4 = new java.util.HashMap<String, Object>();
        v4.put("keyA-27260", "a_Value");
        v4.put("keyB-27260", v2);
        v4.put("keyC", "another_Value");
        v3 = (String) v4.get("keyB-27260");
        v3 = (String) v4.get("keyA-27260");

        String v5 = "";
        String v6 = System.getProperty("os.name");
        if (v6.indexOf("Windows") != -1) {
            v5 = org.owasp.benchmark.helpers.Utils.getOSCommandString("echo");
        }

        Runtime v7 = Runtime.getRuntime();

        try {
            Process v8 = v7.exec(v5 + v3);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v8, response);
        } catch (IOException v9) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v9.getMessage()));
            return;
        }
    }
}
