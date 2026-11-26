<%@ page contentType="text/plain; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"
    import="java.sql.*, kr.smoke.notice.Util" %><%
  // 상태 확인용 (ALB 대상 그룹 · Nginx · Jenkins). DB 까지 붙어야 200.
  try (Connection c = Util.db(); Statement s = c.createStatement();
       ResultSet r = s.executeQuery("SELECT COUNT(*) FROM notice WHERE is_check = 0")) {
    r.next();
    out.print("OK notices=" + r.getInt(1));
  } catch (SQLException e) {
    log("health check failed", e);
    response.setStatus(503);
    out.print("FAIL db");
  }
%>
