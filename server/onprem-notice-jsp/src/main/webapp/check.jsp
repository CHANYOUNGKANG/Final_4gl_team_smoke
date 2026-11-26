<%@ page contentType="text/plain; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"
    import="java.sql.*, java.util.UUID, kr.smoke.notice.Util" %><%
  // 배포 검증 (Jenkins Green 검사): 검증 공지를 쓰고 → 다시 읽고 → 지운다.
  // 사용: curl -fsS -X POST -d "key=$CHECK_KEY" http://<대상>/notice/check.jsp
  if (!"POST".equals(request.getMethod())) { response.setStatus(405); out.print("POST only"); return; }
  String checkKey = Util.env("CHECK_KEY", "");
  if (checkKey.isEmpty() || !checkKey.equals(request.getParameter("key"))) { response.setStatus(403); out.print("FORBIDDEN"); return; }

  String marker = "배포검증-" + UUID.randomUUID();
  try (Connection c = Util.db()) {
    int id;
    try (PreparedStatement ps = c.prepareStatement(
        "INSERT INTO notice (category, title, content, writer, is_check) VALUES ('공지', ?, ?, 'jenkins', 1)",
        Statement.RETURN_GENERATED_KEYS)) {
      ps.setString(1, marker); ps.setString(2, marker);
      ps.executeUpdate();
      try (ResultSet k = ps.getGeneratedKeys()) { k.next(); id = k.getInt(1); }
    }
    String back;
    try (PreparedStatement ps = c.prepareStatement("SELECT content FROM notice WHERE notice_id = ?")) {
      ps.setInt(1, id);
      try (ResultSet r = ps.executeQuery()) { back = r.next() ? r.getString(1) : null; }
    }
    try (PreparedStatement ps = c.prepareStatement("DELETE FROM notice WHERE notice_id = ? AND is_check = 1")) {
      ps.setInt(1, id); ps.executeUpdate();
    }
    if (marker.equals(back)) {
      out.print("CHECK OK write+read+delete");
    } else {
      response.setStatus(500); out.print("CHECK FAIL read-back mismatch");
    }
  } catch (SQLException e) {
    log("deploy check failed", e);
    response.setStatus(503); out.print("CHECK FAIL db");
  }
%>
