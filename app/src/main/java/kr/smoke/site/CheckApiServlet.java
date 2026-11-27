package kr.smoke.site;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * 배포 검증 API 입구 (/api/check/notices, /api/check/notices/{id}).
 * JSP 는 규격상 GET·POST·HEAD 만 받으므로, 실제 메서드(DELETE 등)를 속성에 담고 POST 로 바꿔 JSP 로 넘긴다.
 * 처리 내용은 /WEB-INF/api/check.jsp (DB 접근은 다른 화면과 같은 config.jspf 사용).
 */
public class CheckApiServlet extends HttpServlet {

    public static final String METHOD_ATTR = "check.method";
    /** forward 하면 getRequestURI() 가 JSP 경로로 바뀌므로 원래 주소를 따로 넘긴다 */
    public static final String URI_ATTR = "check.uri";

    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        final String real = req.getMethod();
        req.setAttribute(METHOD_ATTR, real);
        req.setAttribute(URI_ATTR, req.getRequestURI());
        HttpServletRequest wrapped = new HttpServletRequestWrapper(req) {
            @Override
            public String getMethod() {
                return ("GET".equals(real) || "HEAD".equals(real)) ? real : "POST";
            }
        };
        req.getRequestDispatcher("/WEB-INF/api/check.jsp").forward(wrapped, resp);
    }
}
