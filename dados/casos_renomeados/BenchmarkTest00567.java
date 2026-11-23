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

        String v6 = "";
        if (v2 != null) {
            v6 =
                    new String(
                            org.apache.commons.codec.binary.Base64.decodeBase64(
                                    org.apache.commons.codec.binary.Base64.encodeBase64(
                                            v2.getBytes())));
        }

        String v7 = "";
        String v8 = System.getProperty("os.name");
        if (v8.indexOf("Windows") != -1) {
            v7 = org.owasp.benchmark.helpers.Utils.getOSCommandString("echo");
        }

        Runtime v9 = Runtime.getRuntime();

        try {
            Process v10 = v9.exec(v7 + v6);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v10, response);
        } catch (IOException v11) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v11.getMessage()));
            return;
        }
    }
}
