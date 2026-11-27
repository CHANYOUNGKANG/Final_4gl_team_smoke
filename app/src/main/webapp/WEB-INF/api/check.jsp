<%@ page language="java" contentType="application/json; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%!
    static Map<String, Object> checkView(int id, String title, String content) {
        Map<String, Object> m = new LinkedHashMap<String, Object>();
        m.put("id", id);
        m.put("docNo", "CHK-" + id);
        m.put("title", title);
        m.put("content", content);
        m.put("servedBy", servedBy());
        return m;
    }
    static String err(String msg) {
        Map<String, Object> m = new LinkedHashMap<String, Object>();
        m.put("error", msg);
        return SiteUtil.jsonObject(m);
    }
%><%
    /* 배포 검증 API (CI/CD 규격) — 입구는 kr.smoke.site.CheckApiServlet
       POST /api/check/notices        {"title","content"} → 201 + Location, 검증 글(is_check=1) 작성
       GET  /api/check/notices/{id}   → 200 / 없으면 404
       DELETE /api/check/notices/{id} → 204 / 검증 글이 아니면 409 / 없으면 404
       CHECK_TOKEN 이 없으면 전부 404, X-Check-Token 이 다르면 401.
       검증 글은 공개 목록·상세·v_migration_check 에서 빠져요. */
    response.setHeader("Cache-Control", "no-store");
    String method = String.valueOf(request.getAttribute("check.method"));

    if (CHECK_TOKEN.isEmpty()) { response.setStatus(404); out.print(err("not found")); return; }
    if (!SiteUtil.tokenMatches(CHECK_TOKEN, request.getHeader("X-Check-Token"))) {
        response.setStatus(401); out.print(err("unauthorized")); return;
    }
    int id = SiteUtil.checkApiId(String.valueOf(request.getAttribute("check.uri")), request.getContextPath());
    if (id < 0) { response.setStatus(404); out.print(err("not found")); return; }

    Connection conn = null; PreparedStatement ps = null; ResultSet rs = null;
    try {
        conn = getConn();
        if (id == 0) {
            if (!"POST".equals(method)) { response.setStatus(405); response.setHeader("Allow", "POST"); out.print(err("method not allowed")); return; }
            StringBuilder body = new StringBuilder();
            try (BufferedReader r = new BufferedReader(new InputStreamReader(request.getInputStream(), "UTF-8"))) {
                char[] buf = new char[4096]; int n;
                while ((n = r.read(buf)) > 0 && body.length() < 20000) body.append(buf, 0, n);
            }
            String title = nz(SiteUtil.jsonField(body.toString(), "title"));
            String content = nz(SiteUtil.jsonField(body.toString(), "content"));
            if (title.isEmpty() || content.isEmpty() || title.length() > 200 || content.length() > 2000) {
                response.setStatus(400); out.print(err("title(1~200) and content(1~2000) are required")); return;
            }
            ps = conn.prepareStatement(
                "INSERT INTO board (title, writer, content, category, is_pinned, is_check) VALUES (?, 'deploy-check', ?, ?, 0, 1)",
                Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, title);
            ps.setString(2, content);
            ps.setString(3, CATEGORIES[0]);
            ps.executeUpdate();
            rs = ps.getGeneratedKeys();
            int newId = rs.next() ? rs.getInt(1) : -1;
            response.setStatus(201);
            response.setHeader("Location", request.getContextPath() + "/api/check/notices/" + newId);
            application.log("check-api: 검증 글 작성 #" + newId + " servedBy " + DEPLOY_COLOR + "/" + APP_VERSION + "/" + GIT_COMMIT);
            out.print(SiteUtil.jsonObject(checkView(newId, title, content)));
            return;
        }

        ps = conn.prepareStatement("SELECT id, title, content, is_check FROM board WHERE id = ?");
        ps.setInt(1, id);
        rs = ps.executeQuery();
        if (!rs.next()) { response.setStatus(404); out.print(err("not found")); return; }
        String title = rs.getString("title"), content = rs.getString("content");
        boolean isCheck = rs.getInt("is_check") == 1;
        closeQuietly(rs, ps); rs = null; ps = null;

        if ("GET".equals(method) || "HEAD".equals(method)) {
            out.print(SiteUtil.jsonObject(checkView(id, title, content)));
        } else if ("DELETE".equals(method)) {
            if (!isCheck) { response.setStatus(409); out.print(err("only check posts can be deleted")); return; }
            ps = conn.prepareStatement("DELETE FROM board WHERE id = ? AND is_check = 1");
            ps.setInt(1, id);
            ps.executeUpdate();
            application.log("check-api: 검증 글 삭제 #" + id);
            response.setStatus(204);
        } else {
            response.setStatus(405); response.setHeader("Allow", "GET, DELETE"); out.print(err("method not allowed"));
        }
    } catch (Exception e) {
        application.log("check-api 실패", e);
        response.setStatus(503);
        out.print(err("db error"));
    } finally { closeQuietly(rs, ps, conn); }
%>
