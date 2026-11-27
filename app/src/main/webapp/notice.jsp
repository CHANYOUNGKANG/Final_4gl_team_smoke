<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    String pageTitle = "공지 · 자료실";
    String navActive = "notice";

    final int PAGE_SIZE = 10;
    String cat   = nz(request.getParameter("cat"));
    String field = nz(request.getParameter("f"));
    String q     = nz(request.getParameter("q"));
    int pg       = Math.max(1, toInt(request.getParameter("page"), 1));
    if (!validCategory(cat)) cat = "";
    if (!"content".equals(field) && !"writer".equals(field)) field = "title";

    StringBuilder where = new StringBuilder(" WHERE b.is_check = 0");
    List<String> args = new ArrayList<String>();
    if (!cat.isEmpty()) { where.append(" AND b.category = ?"); args.add(cat); }
    if (!q.isEmpty())   { where.append(" AND b.").append(field).append(" LIKE ?"); args.add("%" + q + "%"); }

    List<Map<String, Object>> rows = new ArrayList<Map<String, Object>>();
    int total = 0;
    String dbError = null;
    Connection conn = null; PreparedStatement ps = null; ResultSet rs = null;
    try {
        conn = getConn();
        ps = conn.prepareStatement("SELECT COUNT(*) FROM board b" + where);
        for (int i = 0; i < args.size(); i++) ps.setString(i + 1, args.get(i));
        rs = ps.executeQuery();
        if (rs.next()) total = rs.getInt(1);
        closeQuietly(rs, ps);

        int pages = Math.max(1, (total + PAGE_SIZE - 1) / PAGE_SIZE);
        if (pg > pages) pg = pages;

        ps = conn.prepareStatement(
            "SELECT b.id, b.title, b.writer, b.reg_date, b.category, b.hit, b.is_pinned," +
            " (SELECT COUNT(*) FROM board_file f WHERE f.board_id = b.id) AS fcnt" +
            " FROM board b" + where + " ORDER BY b.is_pinned DESC, b.id DESC LIMIT ? OFFSET ?");
        int i = 1;
        for (String a : args) ps.setString(i++, a);
        ps.setInt(i++, PAGE_SIZE);
        ps.setInt(i, (pg - 1) * PAGE_SIZE);
        rs = ps.executeQuery();
        while (rs.next()) {
            Map<String, Object> m = new HashMap<String, Object>();
            m.put("id", rs.getInt("id"));
            m.put("title", rs.getString("title"));
            m.put("writer", rs.getString("writer"));
            m.put("reg", rs.getTimestamp("reg_date"));
            m.put("cat", rs.getString("category"));
            m.put("hit", rs.getInt("hit"));
            m.put("pin", rs.getInt("is_pinned") == 1);
            m.put("fcnt", rs.getInt("fcnt"));
            rows.add(m);
        }
    } catch (Exception e) {
        dbError = e.getMessage();
    } finally { closeQuietly(rs, ps, conn); }

    int pages = Math.max(1, (total + PAGE_SIZE - 1) / PAGE_SIZE);
    String base = ctx + "/notice.jsp?cat=" + url(cat) + "&f=" + url(field) + "&q=" + url(q) + "&page=";
%>
<%@ include file="/WEB-INF/jspf/header.jspf" %>

<section class="sub-hero">
  <div class="wrap">
    <p class="crumb"><a href="<%= ctx %>/index.jsp">HOME</a><span>/</span>고객지원<span>/</span>공지 · 자료실</p>
    <h1 class="sub-title">공지 · 자료실</h1>
    <p class="sub-lead">서비스 점검 일정과 보안 공지, 배포 자료를 안내합니다.</p>
  </div>
</section>

<section class="board-sec">
  <div class="wrap">
    <div class="board-tools">
      <nav class="tabs" aria-label="분류">
        <a href="<%= ctx %>/notice.jsp" <%= cat.isEmpty() ? "aria-current=\"true\"" : "" %>>전체</a>
        <% for (String c : CATEGORIES) { %>
          <a href="<%= ctx %>/notice.jsp?cat=<%= url(c) %>" <%= c.equals(cat) ? "aria-current=\"true\"" : "" %>><%= esc(c) %></a>
        <% } %>
      </nav>
      <form class="search" action="<%= ctx %>/notice.jsp" method="get" role="search">
        <input type="hidden" name="cat" value="<%= esc(cat) %>">
        <select name="f" aria-label="검색 항목">
          <option value="title" <%= "title".equals(field) ? "selected" : "" %>>제목</option>
          <option value="content" <%= "content".equals(field) ? "selected" : "" %>>내용</option>
          <option value="writer" <%= "writer".equals(field) ? "selected" : "" %>>작성자</option>
        </select>
        <input type="search" name="q" value="<%= esc(q) %>" placeholder="검색어를 입력하세요" aria-label="검색어">
        <button type="submit" aria-label="검색"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg></button>
      </form>
    </div>

    <div class="board-meta">
      <span>총 <b><%= total %></b>건 <% if (!q.isEmpty()) { %>· ‘<%= esc(q) %>’ 검색 결과<% } %></span>
      <a class="pill dark sm" href="<%= ctx %>/write.jsp">글쓰기 </a>
    </div>

    <% if (dbError != null) { %>
      <div class="db-alert"><b>데이터베이스에 연결할 수 없습니다.</b><span>DB_URL 설정과 MariaDB 상태를 확인해 주세요.</span><code><%= esc(dbError) %></code></div>
    <% } else { %>
    <table class="board">
      <colgroup><col class="c-no"><col class="c-cat"><col><col class="c-writer"><col class="c-date"><col class="c-hit"></colgroup>
      <thead><tr><th scope="col">번호</th><th scope="col">분류</th><th scope="col">제목</th><th scope="col">작성자</th><th scope="col">작성일</th><th scope="col">조회</th></tr></thead>
      <tbody>
      <% if (rows.isEmpty()) { %>
        <tr><td colspan="6" class="empty">게시글이 없습니다.</td></tr>
      <% } %>
      <% int no = total - (pg - 1) * PAGE_SIZE;
         for (Map<String, Object> m : rows) { boolean pin = (Boolean) m.get("pin"); String c = (String) m.get("cat"); %>
        <tr class="<%= pin ? "pinned" : "" %>">
          <td class="no"><%= pin ? "<i class=\"pin\">중요</i>" : String.valueOf(no) %></td>
          <td class="cat"><span class="badge <%= catClass(c) %>"><%= esc(c) %></span></td>
          <td class="tit">
            <a href="<%= ctx %>/view.jsp?id=<%= m.get("id") %>"><%= esc(m.get("title")) %></a>
            <% if ((Integer) m.get("fcnt") > 0) { %><svg class="clip" viewBox="0 0 24 24" aria-label="첨부파일 <%= m.get("fcnt") %>개"><path d="M21 11.5l-8.6 8.6a5.5 5.5 0 01-7.8-7.8l9.2-9.2a3.7 3.7 0 015.2 5.2l-9.2 9.2a1.8 1.8 0 01-2.6-2.6l8.5-8.5"/></svg><% } %>
            <% if (isNew((Timestamp) m.get("reg"))) { %><i class="new">N</i><% } %>
            <span class="m-meta"><%= esc(m.get("writer")) %> · <%= fmt((Timestamp) m.get("reg"), "yyyy.MM.dd") %> · 조회 <%= m.get("hit") %></span>
          </td>
          <td class="writer"><%= esc(m.get("writer")) %></td>
          <td class="date"><%= fmt((Timestamp) m.get("reg"), "yyyy.MM.dd") %></td>
          <td class="hit"><%= m.get("hit") %></td>
        </tr>
      <% no--; } %>
      </tbody>
    </table>

    <nav class="paging" aria-label="페이지">
      <% int start = ((pg - 1) / 10) * 10 + 1, end = Math.min(pages, start + 9); %>
      <a href="<%= base %>1" class="pg-arrow <%= pg == 1 ? "off" : "" %>" aria-label="첫 페이지">«</a>
      <a href="<%= base %><%= Math.max(1, pg - 1) %>" class="pg-arrow <%= pg == 1 ? "off" : "" %>" aria-label="이전 페이지">‹</a>
      <% for (int p = start; p <= end; p++) { %>
        <a href="<%= base %><%= p %>" <%= p == pg ? "aria-current=\"page\"" : "" %>><%= p %></a>
      <% } %>
      <a href="<%= base %><%= Math.min(pages, pg + 1) %>" class="pg-arrow <%= pg == pages ? "off" : "" %>" aria-label="다음 페이지">›</a>
      <a href="<%= base %><%= pages %>" class="pg-arrow <%= pg == pages ? "off" : "" %>" aria-label="마지막 페이지">»</a>
    </nav>
    <% } %>
  </div>
</section>

<%@ include file="/WEB-INF/jspf/footer.jspf" %>
