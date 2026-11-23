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
        java.util.Enumeration<String> v2 = request.getHeaderNames();
        while (v2.hasMoreElements()) {
            String v3 = (String) v2.nextElement();

            if (org.owasp.benchmark.helpers.Utils.commonHeaders.contains(v3)) {
                continue;
            }

            java.util.Enumeration<String> v4 = request.getHeaders(v3);
            if (v4 != null && v4.hasMoreElements()) {
                v1 = v3;

                break;
            }
        }

        String v5 = v1;
        StringBuilder v6 = new StringBuilder(v5);
        v6.append(" ItemStuff");
        v6.replace(
                v6.length() - "Chars".length(),
                v6.length(),
                "Chars");
        java.util.HashMap<String, Object> v7 = new java.util.HashMap<String, Object>();
        v7.put("key25969", v6.toString());
        String v8 = (String) v7.get("key25969");
        String v9 = v8.substring(0, v8.length() - 1);
        String v10 =
                new String(
                        org.apache.commons.codec.binary.Base64.decodeBase64(
                                org.apache.commons.codec.binary.Base64.encodeBase64(
                                        v9.getBytes())));
        String v11 = v10.split(" ")[0];
        org.owasp.benchmark.helpers.ThingInterface v12 =
                org.owasp.benchmark.helpers.ThingFactory.createThing();
        String v13 = "barbarians_at_the_gate";
        String v14 = v12.doSomething(v13);

        String v15 = null;
        java.io.FileOutputStream v16 = null;

        try {
            v15 = org.owasp.benchmark.helpers.Utils.TESTFILES_DIR + v14;

            v16 = new java.io.FileOutputStream(v15, false);
            response.getWriter()
                    .println(
                            "Now ready to write to file: "
                                    + org.owasp.esapi.ESAPI.encoder().encodeForHTML(v15));

        } catch (Exception v17) {
            System.out.println("Couldn't open FileOutputStream on file: '" + v15 + "'");

        } finally {
            if (v16 != null) {
                try {
                    v16.close();
                    v16 = null;
                } catch (Exception v17) {

                }
            }
        }
    }
}
