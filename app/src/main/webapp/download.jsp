<%@ page language="java" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    int fid = toInt(request.getParameter("id"), -1);
    String orig = null, stored = null, ctype = null;
    Connection conn = null; PreparedStatement ps = null; ResultSet rs = null;
    try {
        conn = getConn();
        ps = conn.prepareStatement("SELECT orig_name, stored_name, content_type FROM board_file WHERE id = ?");
        ps.setInt(1, fid);
        rs = ps.executeQuery();
        if (rs.next()) { orig = rs.getString(1); stored = rs.getString(2); ctype = rs.getString(3); }
    } catch (Exception e) {
        response.sendError(503, "DB 연결 오류"); return;
    } finally { closeQuietly(rs, ps, conn); }

    if (stored == null) { response.sendError(404); return; }

    // S3 + CloudFront 로 이관된 경우: 파일 서버(files.도메인)로 바로 보냄
    if (!FILE_BASE_URL.isEmpty()) {
        response.sendRedirect(FILE_BASE_URL.replaceAll("/+$", "") + "/" + stored);
        return;
    }

    File root = new File(UPLOAD_DIR).getCanonicalFile();
    File file = new File(root, stored).getCanonicalFile();
    if (!file.getPath().startsWith(root.getPath() + File.separator) || !file.isFile()) { response.sendError(404); return; }

    String encoded = java.net.URLEncoder.encode(orig, "UTF-8").replace("+", "%20");
    response.setContentType(ctype != null && !ctype.isEmpty() ? ctype : "application/octet-stream");
    response.setHeader("Content-Disposition", "attachment; filename=\"" + encoded + "\"; filename*=UTF-8''" + encoded);
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setContentLengthLong(file.length());

    out.clear();
    try (InputStream in = new FileInputStream(file); OutputStream os = response.getOutputStream()) {
        byte[] buf = new byte[8192]; int n;
        while ((n = in.read(buf)) > 0) os.write(buf, 0, n);
    }
    out = pageContext.pushBody();
%>
