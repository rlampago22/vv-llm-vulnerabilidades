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

        String param = "";
        boolean flag = true;
        java.util.Enumeration<String> names = request.getParameterNames();
        while (names.hasMoreElements() && flag) {
            String name = (String) names.nextElement();
            String[] values = request.getParameterValues(name);
            if (values != null) {
                for (int i = 0; i < values.length && flag; i++) {
                    String value = values[i];
                    if (value.equals("CasoAnalisado")) {
                        param = name;
                        flag = false;
                    }
                }
            }
        }

        String a80566 = param;
        StringBuilder b80566 = new StringBuilder(a80566);
        b80566.append(" ItemStuff");
        b80566.replace(
                b80566.length() - "Chars".length(),
                b80566.length(),
                "Chars");
        java.util.HashMap<String, Object> map80566 = new java.util.HashMap<String, Object>();
        map80566.put("key80566", b80566.toString());
        String c80566 = (String) map80566.get("key80566");
        String d80566 = c80566.substring(0, c80566.length() - 1);
        String e80566 =
                new String(
                        org.apache.commons.codec.binary.Base64.decodeBase64(
                                org.apache.commons.codec.binary.Base64.encodeBase64(
                                        d80566.getBytes())));
        String f80566 = e80566.split(" ")[0];
        org.owasp.benchmark.helpers.ThingInterface thing =
                org.owasp.benchmark.helpers.ThingFactory.createThing();
        String g80566 = "barbarians_at_the_gate";
        String bar = thing.doSomething(g80566);

        response.setHeader("X-XSS-Protection", "0");
        response.getWriter().print(bar.toCharArray());
    }
}
