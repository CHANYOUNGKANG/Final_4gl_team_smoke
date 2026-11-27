<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    /* multipart 설정은 WEB-INF/web.xml 의 write-process 서블릿에 있어요. */
    if (!"POST".equalsIgnoreCase(request.getMethod())) { response.sendRedirect(ctx + "/write.jsp"); return; }
    request.setCharacterEncoding("UTF-8");

    Collection<Part> parts;
    try {
        parts = request.getParts();
    } catch (Exception e) {               // 용량 초과 등
        response.sendRedirect(ctx + "/write.jsp?err=file"); return;
    }

    String title    = nz(request.getParameter("title"));
    String writer   = nz(request.getParameter("writer"));
    String content  = nz(request.getParameter("content"));
    String category = nz(request.getParameter("category"));
    boolean pinned  = "1".equals(request.getParameter("is_pinned"));
    if (!validCategory(category)) category = CATEGORIES[0];

    if (!ADMIN_KEY.isEmpty() && !ADMIN_KEY.equals(request.getParameter("admin_key"))) {
        response.sendRedirect(ctx + "/write.jsp?err=key"); return;
    }
    if (title.isEmpty() || writer.isEmpty() || content.isEmpty()) {
        response.sendRedirect(ctx + "/write.jsp?err=input"); return;
    }

    // ---- 첨부파일 검사 ----
    List<Part> uploads = new ArrayList<Part>();
    for (Part p : parts) {
        if (!"files".equals(p.getName()) || p.getSize() == 0) continue;
        String fn = p.getSubmittedFileName();
        if (fn == null || fn.trim().isEmpty()) continue;
        fn = fn.replace('\\', '/');
        fn = fn.substring(fn.lastIndexOf('/') + 1);
        int dot = fn.lastIndexOf('.');
        String ext = dot < 0 ? "" : fn.substring(dot + 1).toLowerCase();
        if (!Arrays.asList(ALLOWED_EXT).contains(ext)) { response.sendRedirect(ctx + "/write.jsp?err=file"); return; }
        uploads.add(p);
    }
    if (uploads.size() > 5) { response.sendRedirect(ctx + "/write.jsp?err=file"); return; }

    Connection conn = null; PreparedStatement ps = null; ResultSet rs = null;
    List<File> written = new ArrayList<File>();
    int newId = -1;
    try {
        conn = getConn();
        conn.setAutoCommit(false);
        ps = conn.prepareStatement(
            "INSERT INTO board (title, writer, content, category, is_pinned) VALUES (?, ?, ?, ?, ?)",
            Statement.RETURN_GENERATED_KEYS);
        ps.setString(1, title);
        ps.setString(2, writer);
        ps.setString(3, content);
        ps.setString(4, category);
        ps.setInt(5, pinned ? 1 : 0);
        ps.executeUpdate();
        rs = ps.getGeneratedKeys();
        if (rs.next()) newId = rs.getInt(1);
        closeQuietly(rs, ps);

        if (!uploads.isEmpty()) {
            String month = new SimpleDateFormat("yyyyMM").format(new java.util.Date());
            File dir = new File(UPLOAD_DIR, month);
            if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("업로드 폴더를 만들 수 없습니다: " + dir);
            ps = conn.prepareStatement(
                "INSERT INTO board_file (board_id, orig_name, stored_name, file_size, content_type, sha256) VALUES (?, ?, ?, ?, ?, ?)");
            for (Part p : uploads) {
                String fn = p.getSubmittedFileName().replace('\\', '/');
                fn = fn.substring(fn.lastIndexOf('/') + 1);
                String ext = fn.substring(fn.lastIndexOf('.') + 1).toLowerCase();
                String stored = month + "/" + UUID.randomUUID().toString().replace("-", "") + "." + ext;
                File target = new File(UPLOAD_DIR, stored);
                java.security.MessageDigest md = java.security.MessageDigest.getInstance("SHA-256");
                try (InputStream in = p.getInputStream(); OutputStream o = new FileOutputStream(target)) {
                    byte[] buf = new byte[8192]; int n;
                    while ((n = in.read(buf)) > 0) { o.write(buf, 0, n); md.update(buf, 0, n); }
                }
                StringBuilder hex = new StringBuilder(64);
                for (byte bt : md.digest()) hex.append(String.format("%02x", bt));
                written.add(target);
                ps.setInt(1, newId);
                ps.setString(2, fn.length() > 255 ? fn.substring(fn.length() - 255) : fn);
                ps.setString(3, stored);
                ps.setLong(4, p.getSize());
                ps.setString(5, p.getContentType());
                ps.setString(6, hex.toString());
                ps.addBatch();
            }
            ps.executeBatch();
        }
        conn.commit();
    } catch (Exception e) {
        if (conn != null) try { conn.rollback(); } catch (Exception ignore) {}
        for (File f : written) f.delete();
        application.log("write_process 실패", e);
        response.sendRedirect(ctx + "/write.jsp?err=db"); return;
    } finally { closeQuietly(rs, ps, conn); }

    response.sendRedirect(ctx + "/view.jsp?id=" + newId);
%>
