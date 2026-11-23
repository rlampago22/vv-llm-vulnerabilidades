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

        String v6 = v2;
        StringBuilder v7 = new StringBuilder(v6);
        v7.append(" ItemStuff");
        v7.replace(
                v7.length() - "Chars".length(),
                v7.length(),
                "Chars");
        java.util.HashMap<String, Object> v8 = new java.util.HashMap<String, Object>();
        v8.put("key6821", v7.toString());
        String v9 = (String) v8.get("key6821");
        String v10 = v9.substring(0, v9.length() - 1);
        String v11 =
                new String(
                        org.apache.commons.codec.binary.Base64.decodeBase64(
                                org.apache.commons.codec.binary.Base64.encodeBase64(
                                        v10.getBytes())));
        String v12 = v11.split(" ")[0];
        org.owasp.benchmark.helpers.ThingInterface v13 =
                org.owasp.benchmark.helpers.ThingFactory.createThing();
        String v14 = "barbarians_at_the_gate";
        String v15 = v13.doSomething(v14);

        String v16 = "";
        String v17 = "";
        String v18 = "";
        String[] args = null;
        String v19 = System.getProperty("os.name");

        if (v19.indexOf("Windows") != -1) {
            v17 = "cmd.exe";
            v18 = "/c";
            v16 = "echo ";
            args = new String[] {v17, v18, v16, v15};
        } else {
            v17 = "sh";
            v18 = "-c";
            v16 = org.owasp.benchmark.helpers.Utils.getOSCommandString("ls ");
            args = new String[] {v17, v18, v16 + v15};
        }

        String[] v20 = {"foo=bar"};

        Runtime v21 = Runtime.getRuntime();

        try {
            Process v22 = v21.exec(args, v20);
            org.owasp.benchmark.helpers.Utils.printOSCommandResults(v22, response);
        } catch (IOException v23) {
            System.out.println("Problem executing cmdi - TestCase");
            response.getWriter()
                    .println(org.owasp.esapi.ESAPI.encoder().encodeForHTML(v23.getMessage()));
            return;
        }
    }
}
