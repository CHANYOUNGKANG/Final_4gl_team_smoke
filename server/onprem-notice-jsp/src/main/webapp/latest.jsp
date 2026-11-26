<%@ page contentType="application/json; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"
    import="java.sql.*, kr.smoke.notice.Util" %><%
  // 메인 페이지의 "최신 공지" 칸이 불러가는 최신 글 목록 (JSON)
  // GET /notice/latest.jsp?n=5
  int n = Math.max(1, Math.min(10, Util.toInt(request.getParameter("n"), 5)));
  response.setHeader("Cache-Control", "no-store");
  StringBuilder b = new StringBuilder("[");
  try (Connection c = Util.db();
       PreparedStatement ps = c.prepareStatement(
         "SELECT n.notice_id, n.category, n.title, n.created_at,"
         + " (SELECT COUNT(*) FROM attachment a WHERE a.notice_id = n.notice_id) AS files"
         + " FROM notice n WHERE n.is_check = 0 ORDER BY n.created_at DESC, n.notice_id DESC LIMIT ?")) {
    ps.setInt(1, n);
    try (ResultSet r = ps.executeQuery()) {
      boolean first = true;
      while (r.next()) {
        if (!first) b.append(',');
        first = false;
        b.append("{\"id\":").append(r.getInt(1))
         .append(",\"category\":").append(Util.json(r.getString(2)))
         .append(",\"title\":").append(Util.json(r.getString(3)))
         .append(",\"date\":").append(Util.json(r.getTimestamp(4).toLocalDateTime().toLocalDate().toString()))
         .append(",\"files\":").append(r.getInt(5))
         .append('}');
      }
    }
    b.append(']');
    out.print(b);
  } catch (SQLException e) {
    log("latest notices failed", e);
    response.setStatus(503);
    out.print("[]");
  }
%>
