<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" isErrorPage="true" %>
<%@ include file="/WEB-INF/inc/head.jspf" %>
<%
  Object code = request.getAttribute("jakarta.servlet.error.status_code");
  Object msg  = request.getAttribute("jakarta.servlet.error.message");
  String text = (msg != null && !msg.toString().isBlank()) ? msg.toString()
              : ("404".equals(String.valueOf(code)) ? "찾는 글이 없습니다." : "요청을 처리하지 못했습니다.");
%>
<h1>오류 <%= code != null ? code : "" %></h1>
<div class="err"><%= kr.smoke.notice.Util.esc(text) %></div>
<p style="margin-top:20px"><a class="btn" href="<%= request.getContextPath() %>/">목록으로</a></p>
<%@ include file="/WEB-INF/inc/foot.jspf" %>
