<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    String pageTitle = "공지 · 자료실";
    String navActive = "notice";

    int id = toInt(request.getParameter("id"), -1);
    Map<String, Object> post = null;
    List<Map<String, Object>> files = new ArrayList<Map<String, Object>>();
    Map<String, Object> prev = null, next = null;
    String dbError = null;

    Connection conn = null; PreparedStatement ps = null; ResultSet rs = null;
    try {
        conn = getConn();
        ps = conn.prepareStatement("UPDATE board SET hit = hit + 1 WHERE id = ? AND is_check = 0");
        ps.setInt(1, id);
        ps.executeUpdate();
        closeQuietly(ps);

        ps = conn.prepareStatement("SELECT id, title, writer, content, reg_date, category, hit, is_pinned FROM board WHERE id = ? AND is_check = 0");
        ps.setInt(1, id);
        rs = ps.executeQuery();
        if (rs.next()) {
            post = new HashMap<String, Object>();
            post.put("title", rs.getString("title"));
            post.put("writer", rs.getString("writer"));
            post.put("content", rs.getString("content"));
            post.put("reg", rs.getTimestamp("reg_date"));
            post.put("cat", rs.getString("category"));
            post.put("hit", rs.getInt("hit"));
            post.put("pin", rs.getInt("is_pinned") == 1);
        }
        closeQuietly(rs, ps);

        if (post != null) {
            ps = conn.prepareStatement("SELECT id, orig_name, file_size, sha256 FROM board_file WHERE board_id = ? ORDER BY id");
            ps.setInt(1, id);
            rs = ps.executeQuery();
            while (rs.next()) {
                Map<String, Object> f = new HashMap<String, Object>();
                f.put("id", rs.getInt("id"));
                f.put("name", rs.getString("orig_name"));
                f.put("size", rs.getLong("file_size"));
                f.put("sha", rs.getString("sha256"));
                files.add(f);
            }
            closeQuietly(rs, ps);

            ps = conn.prepareStatement("SELECT id, title FROM board WHERE id < ? AND is_check = 0 ORDER BY id DESC LIMIT 1");
            ps.setInt(1, id);
            rs = ps.executeQuery();
            if (rs.next()) { prev = new HashMap<String, Object>(); prev.put("id", rs.getInt(1)); prev.put("title", rs.getString(2)); }
            closeQuietly(rs, ps);

            ps = conn.prepareStatement("SELECT id, title FROM board WHERE id > ? AND is_check = 0 ORDER BY id ASC LIMIT 1");
            ps.setInt(1, id);
            rs = ps.executeQuery();
            if (rs.next()) { next = new HashMap<String, Object>(); next.put("id", rs.getInt(1)); next.put("title", rs.getString(2)); }
        }
    } catch (Exception e) {
        dbError = e.getMessage();
    } finally { closeQuietly(rs, ps, conn); }

    if (post == null && dbError == null) response.setStatus(404);
%>
<%@ include file="/WEB-INF/jspf/header.jspf" %>

<section class="sub-hero slim">
  <div class="wrap">
    <p class="crumb"><a href="<%= ctx %>/index.jsp">HOME</a><span>/</span><a href="<%= ctx %>/notice.jsp">공지 · 자료실</a></p>
    <h1 class="sub-title">공지 · 자료실</h1>
  </div>
</section>

<section class="board-sec">
  <div class="wrap narrow">
  <% if (dbError != null) { %>
    <div class="db-alert"><b>데이터베이스에 연결할 수 없습니다.</b><code><%= esc(dbError) %></code></div>
  <% } else if (post == null) { %>
    <div class="empty-box">요청하신 게시글을 찾을 수 없습니다. <a href="<%= ctx %>/notice.jsp">목록으로 →</a></div>
  <% } else { String c = (String) post.get("cat"); %>
    <article class="post">
      <header class="post-head">
        <div class="post-badges">
          <span class="badge <%= catClass(c) %>"><%= esc(c) %></span>
          <% if ((Boolean) post.get("pin")) { %><i class="pin">중요</i><% } %>
        </div>
        <h2 class="post-title"><%= esc(post.get("title")) %></h2>
        <dl class="post-meta">
          <div><dt>작성자</dt><dd><%= esc(post.get("writer")) %></dd></div>
          <div><dt>작성일</dt><dd><%= fmt((Timestamp) post.get("reg"), "yyyy.MM.dd HH:mm") %></dd></div>
          <div><dt>조회</dt><dd><%= post.get("hit") %></dd></div>
        </dl>
      </header>
      <div class="post-body"><%= escBr((String) post.get("content")) %></div>
      <% if (!files.isEmpty()) { %>
      <div class="post-files">
        <h3>첨부파일 <span><%= files.size() %></span></h3>
        <ul>
        <% for (Map<String, Object> f : files) { %>
          <li><a href="<%= ctx %>/download.jsp?id=<%= f.get("id") %>">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m0 0l-5-5m5 5l5-5M4 19h16"/></svg>
            <span class="fn"><%= esc(f.get("name")) %></span><span class="fs"><%= fmtSize((Long) f.get("size")) %></span><% if (f.get("sha") != null) { %><span class="fs" title="SHA-256 <%= esc(f.get("sha")) %>">SHA-256 <%= esc(String.valueOf(f.get("sha")).substring(0, 12)) %>…</span><% } %>
          </a></li>
        <% } %>
        </ul>
      </div>
      <% } %>
      <nav class="post-nav" aria-label="이전·다음 글">
        <div><span>이전 글</span><% if (prev != null) { %><a href="<%= ctx %>/view.jsp?id=<%= prev.get("id") %>"><%= esc(prev.get("title")) %></a><% } else { %><em>이전 글이 없습니다.</em><% } %></div>
        <div><span>다음 글</span><% if (next != null) { %><a href="<%= ctx %>/view.jsp?id=<%= next.get("id") %>"><%= esc(next.get("title")) %></a><% } else { %><em>다음 글이 없습니다.</em><% } %></div>
      </nav>
      <div class="post-actions"><a class="pill dark" href="<%= ctx %>/notice.jsp">목록으로</a></div>
    </article>
  <% } %>
  </div>
</section>

<%@ include file="/WEB-INF/jspf/footer.jspf" %>
