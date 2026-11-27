package kr.smoke.site;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * /notices/{id} → 공지 상세(view.jsp?id={id}).
 * 검증 글(is_check=1)·없는 글은 view.jsp 가 404 를 돌려준다 (CI/CD 자동 검증 규격).
 */
public class NoticeDetailServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        int id = SiteUtil.noticeId(req.getPathInfo());
        if (id == 0) { resp.sendRedirect(req.getContextPath() + "/notices"); return; }
        if (id < 0) { resp.sendError(HttpServletResponse.SC_NOT_FOUND); return; }
        req.getRequestDispatcher("/view.jsp?id=" + id).forward(req, resp);
    }
}
