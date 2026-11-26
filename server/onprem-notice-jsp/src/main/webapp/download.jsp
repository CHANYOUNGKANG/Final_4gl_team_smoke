<%@ page trimDirectiveWhitespaces="true" pageEncoding="UTF-8"
    import="java.sql.*, java.nio.file.*, java.io.*, java.net.URLEncoder,
            java.nio.charset.StandardCharsets, kr.smoke.notice.Util" %><%
  int fid = Util.toInt(request.getParameter("fid"), -1);
  String stored = null, orig = null, mime = null;
  try (Connection c = Util.db();
       PreparedStatement ps = c.prepareStatement(
         "SELECT a.stored_name, a.orig_name, a.mime_type FROM attachment a"
         + " JOIN notice n ON n.notice_id = a.notice_id WHERE a.file_id = ? AND n.is_check = 0")) {
    ps.setInt(1, fid);
    try (ResultSet r = ps.executeQuery()) {
      if (r.next()) { stored = r.getString(1); orig = r.getString(2); mime = r.getString(3); }
    }
  } catch (SQLException e) {
    log("download lookup failed", e);
    response.sendError(500); return;
  }
  if (stored == null) { response.sendError(404); return; }

  Path dir = Paths.get(Util.env("UPLOAD_DIR", "/var/smoke/attach")).toAbsolutePath().normalize();
  Path f = dir.resolve(stored).normalize();
  if (!f.startsWith(dir) || !Files.isRegularFile(f)) { response.sendError(404); return; }

  out.clear();
  out = pageContext.pushBody();
  response.setContentType(mime != null ? mime : "application/octet-stream");
  response.setContentLengthLong(Files.size(f));
  response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''"
      + URLEncoder.encode(orig, StandardCharsets.UTF_8).replace("+", "%20"));
  response.setHeader("X-Content-Type-Options", "nosniff");
  try (OutputStream os = response.getOutputStream()) {
    Files.copy(f, os);
  }
%>
