<%@ page language="java" contentType="application/json; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    /* ALB · Kubernetes Probe · Jenkins 상태 검사 (CI/CD 규격)
       GET /health  →  200 {"status":"UP","db":"UP","storage":"UP","app":…,"version":…,"color":…,"commit":…}
                       DB 나 첨부 저장소 중 하나라도 안 되면 503, status DOWN */
    response.setHeader("Cache-Control", "no-store");
    String db = "DOWN";
    Connection conn = null; Statement st = null;
    try {
        conn = getConn();
        st = conn.createStatement();
        st.execute("SELECT 1");
        db = "UP";
    } catch (Exception e) {
        application.log("health: DB 확인 실패 - " + e.getMessage());
    } finally { closeQuietly(st, conn); }
    String storage = storageReady() ? "UP" : "DOWN";
    boolean up = "UP".equals(db) && "UP".equals(storage);
    if (!up) response.setStatus(503);

    Map<String, Object> body = new LinkedHashMap<String, Object>();
    body.put("status", up ? "UP" : "DOWN");
    body.put("db", db);
    body.put("storage", storage);
    body.put("app", SiteUtil.APP_NAME);
    body.putAll(servedBy());
    out.print(SiteUtil.jsonObject(body));
%>
