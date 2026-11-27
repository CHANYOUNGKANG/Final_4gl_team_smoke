<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    String pageTitle = "글쓰기";
    String navActive = "notice";
    String err = request.getParameter("err");
    String errMsg = null;
    if ("key".equals(err))   errMsg = "관리자 키가 올바르지 않습니다.";
    else if ("input".equals(err)) errMsg = "제목, 작성자, 내용을 모두 입력해 주세요.";
    else if ("file".equals(err))  errMsg = "허용되지 않는 파일 형식이거나 파일이 너무 큽니다. (파일당 20MB, 최대 5개)";
    else if ("db".equals(err))    errMsg = "저장 중 오류가 발생했습니다. DB 연결을 확인해 주세요.";
%>
<%@ include file="/WEB-INF/jspf/header.jspf" %>

<section class="sub-hero slim">
  <div class="wrap">
    <p class="crumb"><a href="<%= ctx %>/index.jsp">HOME</a><span>/</span><a href="<%= ctx %>/notice.jsp">공지 · 자료실</a><span>/</span>글쓰기</p>
    <h1 class="sub-title">새 글 작성</h1>
  </div>
</section>

<section class="board-sec">
  <div class="wrap narrow">
    <form class="write-form" action="<%= ctx %>/write_process.jsp" method="post" enctype="multipart/form-data">
      <% if (errMsg != null) { %><div class="form-err" role="alert"><%= esc(errMsg) %></div><% } %>
      <div class="f-row two">
        <label><span>분류</span>
          <select name="category">
            <% for (String c : CATEGORIES) { %><option value="<%= esc(c) %>"><%= esc(c) %></option><% } %>
          </select>
        </label>
        <label><span>작성자 <i>*</i></span><input type="text" name="writer" maxlength="50" required placeholder="이름 또는 부서"></label>
      </div>
      <div class="f-row"><label><span>제목 <i>*</i></span><input type="text" name="title" maxlength="200" required placeholder="제목을 입력하세요"></label></div>
      <div class="f-row"><label><span>내용 <i>*</i></span><textarea name="content" rows="12" required placeholder="내용을 입력하세요"></textarea></label></div>
      <div class="f-row">
        <span class="f-lbl">첨부파일</span>
        <label class="drop" id="drop">
          <input type="file" name="files" multiple id="fileInput" accept=".<%= String.join(",.", ALLOWED_EXT) %>">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V4m0 0l-5 5m5-5l5 5M4 20h16"/></svg>
          <b>파일을 끌어다 놓거나 클릭해서 선택</b>
          <small>파일당 20MB · 최대 5개 · PDF, HWP, Office, 이미지, ZIP</small>
          <ul class="drop-list" id="dropList"></ul>
        </label>
      </div>
      <div class="f-row inline">
        <label class="check"><input type="checkbox" name="is_pinned" value="1"><span>중요 공지로 상단 고정</span></label>
        <% if (!ADMIN_KEY.isEmpty()) { %>
          <label class="key"><span>관리자 키 <i>*</i></span><input type="password" name="admin_key" required autocomplete="off"></label>
        <% } %>
      </div>
      <div class="form-actions">
        <a class="pill ghost" href="<%= ctx %>/notice.jsp">취소</a>
        <button type="submit" class="pill">등록하기</button>
      </div>
    </form>
  </div>
</section>

<%@ include file="/WEB-INF/jspf/footer.jspf" %>
