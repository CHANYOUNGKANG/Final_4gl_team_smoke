<%@ page language="java" contentType="application/json; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    /* GET /version → {"app":"haedeun-notice","version":…,"color":…,"commit":…}  (블루그린 전환 확인용) */
    response.setHeader("Cache-Control", "no-store");
    Map<String, Object> body = new LinkedHashMap<String, Object>();
    body.put("app", SiteUtil.APP_NAME);
    body.putAll(servedBy());
    out.print(SiteUtil.jsonObject(body));
%>
