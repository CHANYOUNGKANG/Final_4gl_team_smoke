<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"
    import="java.sql.*, java.nio.file.*, java.io.*, java.security.*, java.util.*,
            jakarta.servlet.http.Part, kr.smoke.notice.Util" %>
<%
  if (!"POST".equals(request.getMethod())) { response.sendRedirect("write.jsp"); return; }

  String writeKey = Util.env("WRITE_KEY", "");
  if (writeKey.isEmpty() || !writeKey.equals(request.getParameter("key"))) {
    response.sendError(403, "관리 키가 맞지 않습니다.");
    return;
  }

  String category = request.getParameter("category");
  String title    = request.getParameter("title");
  String writer   = request.getParameter("writer");
  String content  = request.getParameter("content");
  if (!Util.validCategory(category) || title == null || title.isBlank() || title.length() > 200
      || writer == null || writer.isBlank() || writer.length() > 50
      || content == null || content.isBlank()) {
    response.sendError(400, "입력값을 확인해 주세요.");
    return;
  }

  List<Part> uploads = new ArrayList<>();
  for (Part p : request.getParts()) {
    if ("files".equals(p.getName()) && p.getSize() > 0 && !Util.baseName(p.getSubmittedFileName()).isEmpty()) uploads.add(p);
  }
  if (uploads.size() > 3) { response.sendError(400, "첨부파일은 3개까지 올릴 수 있습니다."); return; }

  Path dir = Paths.get(Util.env("UPLOAD_DIR", "/var/smoke/attach"));
  List<Path> written = new ArrayList<>();
  int noticeId = -1;

  try (Connection c = Util.db()) {
    c.setAutoCommit(false);
    try {
      try (PreparedStatement ps = c.prepareStatement(
          "INSERT INTO notice (category, title, content, writer) VALUES (?, ?, ?, ?)",
          Statement.RETURN_GENERATED_KEYS)) {
        ps.setString(1, category); ps.setString(2, title.trim());
        ps.setString(3, content);  ps.setString(4, writer.trim());
        ps.executeUpdate();
        try (ResultSet k = ps.getGeneratedKeys()) { k.next(); noticeId = k.getInt(1); }
      }

      for (Part p : uploads) {
        String orig   = Util.baseName(p.getSubmittedFileName());
        String stored = UUID.randomUUID() + Util.safeExt(orig);
        Path target   = dir.resolve(stored);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        try (InputStream in = new DigestInputStream(p.getInputStream(), md)) {
          Files.copy(in, target);
        }
        written.add(target);
        try (PreparedStatement ps = c.prepareStatement(
            "INSERT INTO attachment (notice_id, orig_name, stored_name, file_size, mime_type, sha256)"
            + " VALUES (?, ?, ?, ?, ?, ?)")) {
          ps.setInt(1, noticeId); ps.setString(2, orig); ps.setString(3, stored);
          ps.setLong(4, Files.size(target)); ps.setString(5, p.getContentType());
          ps.setString(6, Util.hex(md.digest()));
          ps.executeUpdate();
        }
      }
      c.commit();
    } catch (Exception e) {
      c.rollback();
      for (Path w : written) { try { Files.deleteIfExists(w); } catch (IOException ignore) {} }
      throw e;
    }
  } catch (Exception e) {
    log("notice write failed", e);
    response.sendError(500, "저장하지 못했습니다.");
    return;
  }
  response.sendRedirect("view.jsp?id=" + noticeId);
%>
