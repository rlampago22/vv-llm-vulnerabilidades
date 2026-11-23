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

        String v1 = request.getParameter("CasoAnalisado");
        if (v1 == null) v1 = "";

        String v2 = metodo1(request, v1);

        String v3 = "";
        String v4 = "";
        String v5 = "";
        String[] args = null;
        String v6 = System.getProperty("os.name");

        if (v6.indexOf("Windows") != -1) {
            v4 = "cmd.exe";
            v5 = "/c";
            v3 = "echo ";
            args = new String[] {v4, v5, v3, v2};
        } else {
            v4 = "sh";
            v5 = "-c";
            v3 = org.owasp.benchmark.helpers.Utils.getOSCommandString("ls ");
            args = new String[] {v4, v5, v3 + v2};
        }

        String[] v7 = {"foo=bar"};

        Runtime v8 = Runtime.getRuntime();

        try {
            Process v9 = v8.exec(args, v7);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v9, response);
        } catch (IOException v10) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v10.getMessage()));
            return;
        }
    }

    private static String metodo1(HttpServletRequest request, String v1)
            throws ServletException, IOException {

        String v2;

        int num = 106;

        v2 = (7 * 18) + num > 200 ? "This_should_always_happen" : v1;

        return v2;
    }
}
