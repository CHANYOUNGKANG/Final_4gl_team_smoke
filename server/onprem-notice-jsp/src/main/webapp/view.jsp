<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"
    import="java.sql.*, kr.smoke.notice.Util" %>
<%
  int id = Util.toInt(request.getParameter("id"), -1);
  String category = null, title = null, writer = null, content = null;
  int views = 0; Timestamp created = null;
  java.util.List<String[]> files = new java.util.ArrayList<>();
  boolean dbError = false;
  try (Connection c = Util.db()) {
    try (PreparedStatement ps = c.prepareStatement(
        "UPDATE notice SET view_count = view_count + 1 WHERE notice_id = ? AND is_check = 0")) {
      ps.setInt(1, id); ps.executeUpdate();
    }
    try (PreparedStatement ps = c.prepareStatement(
        "SELECT category, title, writer, content, view_count, created_at FROM notice WHERE notice_id = ? AND is_check = 0")) {
      ps.setInt(1, id);
      try (ResultSet r = ps.executeQuery()) {
        if (r.next()) {
          category = r.getString(1); title = r.getString(2); writer = r.getString(3);
          content = r.getString(4); views = r.getInt(5); created = r.getTimestamp(6);
        }
      }
    }
    if (title != null) {
      try (PreparedStatement ps = c.prepareStatement(
          "SELECT file_id, orig_name, file_size, sha256 FROM attachment WHERE notice_id = ? ORDER BY file_id")) {
        ps.setInt(1, id);
        try (ResultSet r = ps.executeQuery()) {
          while (r.next()) files.add(new String[]{ r.getString(1), r.getString(2), Util.size(r.getLong(3)), r.getString(4) });
        }
      }
    }
  } catch (SQLException e) {
    log("notice view failed", e);
    dbError = true;
  }
  if (!dbError && title == null) { response.sendError(404); return; }
%>
<%@ include file="/WEB-INF/inc/head.jspf" %>
<% if (dbError) { %>
<div class="err">글을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>
<% } else { %>
<p><span class="cat"><%= Util.esc(category) %></span></p>
<h1><%= Util.esc(title) %></h1>
<div class="meta"><%= Util.esc(writer) %> · <%= created.toLocalDateTime().toString().replace('T', ' ').substring(0, 16) %> · 조회 <%= views %></div>
<div class="body"><%= Util.esc(content) %></div>
<% if (!files.isEmpty()) { %>
<div class="files"><b>첨부파일</b>
  <ul>
  <% for (String[] f : files) { %>
    <li><a href="download.jsp?fid=<%= f[0] %>"><%= Util.esc(f[1]) %></a> (<%= f[2] %>)
        <br><span class="hash">SHA-256 <%= f[3] %></span></li>
  <% } %>
  </ul>
</div>
<% } %>
<% } %>
<p style="margin-top:24px"><a class="btn" href="<%= request.getContextPath() %>/">목록</a></p>
<%@ include file="/WEB-INF/inc/foot.jspf" %>
