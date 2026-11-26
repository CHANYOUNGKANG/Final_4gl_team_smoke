<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"
    import="kr.smoke.notice.Util" %>
<%@ include file="/WEB-INF/inc/head.jspf" %>
<h1>글쓰기</h1>
<form method="post" action="write_ok.jsp" enctype="multipart/form-data">
  <label for="category">분류</label>
  <select id="category" name="category" required>
  <% for (String c : Util.CATEGORIES) { %><option><%= c %></option><% } %>
  </select>

  <label for="title">제목</label>
  <input type="text" id="title" name="title" maxlength="200" required>

  <label for="writer">작성 부서</label>
  <input type="text" id="writer" name="writer" maxlength="50" required placeholder="예: 품질보증팀">

  <label for="content">내용</label>
  <textarea id="content" name="content" required></textarea>

  <label for="files">첨부파일 (최대 3개, 파일당 20MB)</label>
  <input type="file" id="files" name="files" multiple>

  <label for="key">관리 키</label>
  <input type="password" id="key" name="key" required autocomplete="off">

  <p style="margin-top:22px"><button class="btn" type="submit">등록</button>
     <a href="<%= request.getContextPath() %>/" style="margin-left:10px">취소</a></p>
</form>
<%@ include file="/WEB-INF/inc/foot.jspf" %>
