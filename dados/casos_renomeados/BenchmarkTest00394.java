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

        String v2 = "alsoitem";
        if (v1 != null) {
            java.util.List<String> v3 = new java.util.ArrayList<String>();
            v3.add("item");
            v3.add(v1);
            v3.add("moreitem");

            v3.remove(0);

            v2 = v3.get(1);
        }

        response.setHeader("X-XSS-Protection", "0");
        int length = 1;
        if (v2 != null) {
            length = v2.length();
            response.getWriter().write(v2, 0, length);
        }
    }
}
