<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" isErrorPage="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    String pageTitle = "페이지를 찾을 수 없습니다";
    String navActive = "";
    Object code = request.getAttribute("javax.servlet.error.status_code");
    if (code == null) code = request.getAttribute("jakarta.servlet.error.status_code");
    if (code == null) code = response.getStatus();
%>
<%@ include file="/WEB-INF/jspf/header.jspf" %>
<section class="sub-hero err">
  <div class="wrap">
    <p class="err-code"><%= esc(code) %></p>
    <h1 class="sub-title">요청하신 페이지를 열 수 없습니다.</h1>
    <p class="sub-lead">주소가 바뀌었거나 일시적인 문제일 수 있습니다.</p>
    <div class="hero-cta"><a class="pill" href="<%= ctx %>/index.jsp">홈으로</a><a class="pill ghost" href="<%= ctx %>/notice.jsp">공지 · 자료실</a></div>
  </div>
</section>
<%@ include file="/WEB-INF/jspf/footer.jspf" %>
