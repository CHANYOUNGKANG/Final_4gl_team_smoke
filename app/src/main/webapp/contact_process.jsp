<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" trimDirectiveWhitespaces="true"%>
<%@ include file="/WEB-INF/jspf/config.jspf" %>
<%
    if (!"POST".equalsIgnoreCase(request.getMethod())) { response.sendRedirect(ctx + "/index.jsp#contact"); return; }
    request.setCharacterEncoding("UTF-8");

    String company = nz(request.getParameter("company"));
    String name    = nz(request.getParameter("name"));
    String email   = nz(request.getParameter("email"));
    String phone   = nz(request.getParameter("phone"));
    String topic   = nz(request.getParameter("topic"));
    String message = nz(request.getParameter("message"));

    String result = "1";
    if (name.isEmpty() || email.isEmpty() || message.isEmpty() || !email.matches("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")) {
        result = "0";
    } else {
        Connection conn = null; PreparedStatement ps = null;
        try {
            conn = getConn();
            ps = conn.prepareStatement("INSERT INTO inquiry (company, name, email, phone, topic, message) VALUES (?, ?, ?, ?, ?, ?)",
                                       Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, company.length() > 100 ? company.substring(0, 100) : company);
            ps.setString(2, name.length() > 50 ? name.substring(0, 50) : name);
            ps.setString(3, email.length() > 120 ? email.substring(0, 120) : email);
            ps.setString(4, phone.length() > 40 ? phone.substring(0, 40) : phone);
            ps.setString(5, topic.length() > 40 ? topic.substring(0, 40) : topic);
            ps.setString(6, message.length() > 4000 ? message.substring(0, 4000) : message);
            ps.executeUpdate();
            int inqId = -1;
            try (ResultSet gk = ps.getGeneratedKeys()) { if (gk.next()) inqId = gk.getInt(1); }

            // 접수 저장이 끝난 뒤 담당자 메일 알림. 메일이 실패해도 접수는 유지하고 로그만 남겨요.
            if (!MAIL_TO.isEmpty()) {
                String when = new SimpleDateFormat("yyyy-MM-dd HH:mm").format(new java.util.Date());
                String subject = "[홈페이지 문의 #" + inqId + "] " + (topic.isEmpty() ? "일반" : topic) + " - "
                               + (company.isEmpty() ? "" : company + " ") + name;
                String body = "홈페이지 문의가 접수되었습니다.\n\n"
                            + "접수 번호 : " + inqId + "\n"
                            + "접수 시각 : " + when + "\n"
                            + "회사명    : " + company + "\n"
                            + "담당자    : " + name + "\n"
                            + "이메일    : " + email + "\n"
                            + "연락처    : " + phone + "\n"
                            + "문의 분야 : " + topic + "\n\n"
                            + "[문의 내용]\n" + message + "\n";
                try {
                    sendMail(MAIL_TO, email, subject, body);
                    application.log("contact_process 메일 발송 성공 #" + inqId + " -> " + MAIL_TO);
                } catch (Exception me) {
                    application.log("contact_process 메일 발송 실패 #" + inqId, me);
                }
            }
        } catch (Exception e) {
            application.log("contact_process 실패", e);
            result = "0";
        } finally { closeQuietly(ps, conn); }
    }
    response.sendRedirect(ctx + "/index.jsp?sent=" + result + "#contact");
%>
