<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"
    import="java.sql.*, kr.smoke.notice.Util" %>
<%@ include file="/WEB-INF/inc/head.jspf" %>
<%
  String cat = request.getParameter("cat");
  if (!Util.validCategory(cat)) cat = null;
  String base = request.getContextPath() + "/";
%>
<h1>공지·자료실</h1>
<div class="tabs">
  <a href="<%= base %>" class="<%= cat == null ? "on" : "" %>">전체</a>
<% for (String c : Util.CATEGORIES) { %>
  <a href="<%= base %>?cat=<%= java.net.URLEncoder.encode(c, "UTF-8") %>" class="<%= c.equals(cat) ? "on" : "" %>"><%= c %></a>
<% } %>
</div>
<table>
  <thead><tr><th class="c">번호</th><th class="c">분류</th><th>제목</th><th class="c">작성</th><th class="c">첨부</th><th class="c">조회</th><th class="c">등록일</th></tr></thead>
  <tbody>
<%
  String sql = "SELECT n.notice_id, n.category, n.title, n.writer, n.is_pinned, n.view_count, n.created_at,"
             + " (SELECT COUNT(*) FROM attachment a WHERE a.notice_id = n.notice_id) AS files"
             + " FROM notice n WHERE n.is_check = 0" + (cat != null ? " AND n.category = ?" : "")
             + " ORDER BY n.is_pinned DESC, n.created_at DESC LIMIT 100";
  int rows = 0;
  try (Connection c = Util.db(); PreparedStatement ps = c.prepareStatement(sql)) {
    if (cat != null) ps.setString(1, cat);
    try (ResultSet r = ps.executeQuery()) {
      while (r.next()) {
        rows++;
%>
    <tr>
      <td class="c"><%= r.getInt("notice_id") %></td>
      <td class="c"><span class="cat"><%= Util.esc(r.getString("category")) %></span></td>
      <td><% if (r.getInt("is_pinned") == 1) { %><span class="pin">[고정]</span><% } %><a href="view.jsp?id=<%= r.getInt("notice_id") %>"><%= Util.esc(r.getString("title")) %></a></td>
      <td class="c"><%= Util.esc(r.getString("writer")) %></td>
      <td class="c"><%= r.getInt("files") > 0 ? "📎 " + r.getInt("files") : "" %></td>
      <td class="c"><%= r.getInt("view_count") %></td>
      <td class="c"><%= r.getTimestamp("created_at").toLocalDateTime().toLocalDate() %></td>
    </tr>
<%
      }
    }
  } catch (SQLException e) {
    log("notice list failed", e);
    rows = -1;
%>
    <tr><td colspan="7"><div class="err">목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div></td></tr>
<%
  }
  if (rows == 0) {
%>
    <tr><td colspan="7" class="c">등록된 글이 없습니다.</td></tr>
<% } %>
  </tbody>
</table>
<%@ include file="/WEB-INF/inc/foot.jspf" %>
