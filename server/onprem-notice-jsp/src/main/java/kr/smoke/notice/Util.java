package kr.smoke.notice;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.HexFormat;
import java.util.List;

/** 공지 앱 공통 기능. JSP 에서 import 해서 쓴다. 설정은 모두 환경 변수로 받는다. */
public final class Util {

    /** DB 의 ck_category 제약과 같은 목록 */
    public static final List<String> CATEGORIES = List.of("공지", "납품일정", "품질인증", "도면");

    private Util() {}

    public static String env(String key, String def) {
        String v = System.getenv(key);
        return (v == null || v.isBlank()) ? def : v.trim();
    }

    public static Connection db() throws SQLException {
        String url = "jdbc:mariadb://" + env("DB_HOST", "localhost") + ":" + env("DB_PORT", "3306")
                + "/" + env("DB_NAME", "smoke_board");
        return DriverManager.getConnection(url, env("DB_USER", "smoke"), env("DB_PASS", ""));
    }

    /** HTML 출력용 이스케이프 (XSS 방지) */
    public static String esc(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length() + 16);
        for (char c : s.toCharArray()) {
            switch (c) {
                case '<' -> b.append("&lt;");
                case '>' -> b.append("&gt;");
                case '&' -> b.append("&amp;");
                case '"' -> b.append("&quot;");
                case '\'' -> b.append("&#39;");
                default -> b.append(c);
            }
        }
        return b.toString();
    }

    /** JSON 문자열 값으로 쓸 수 있게 따옴표 포함해서 이스케이프 */
    public static String json(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder(s.length() + 8).append('"');
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> b.append("\\\"");
                case '\\' -> b.append("\\\\");
                case '\n' -> b.append("\\n");
                case '\r' -> b.append("\\r");
                case '\t' -> b.append("\\t");
                case '<' -> b.append("\\u003c");
                case '>' -> b.append("\\u003e");
                case '&' -> b.append("\\u0026");
                default -> {
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
                }
            }
        }
        return b.append('"').toString();
    }

    public static boolean validCategory(String c) {
        return c != null && CATEGORIES.contains(c);
    }

    /** 브라우저가 보낸 파일 이름에서 경로를 떼어 낸다 (C:\a\b.pdf, ../x 등) */
    public static String baseName(String submitted) {
        if (submitted == null) return "";
        String s = submitted.replace('\\', '/');
        s = s.substring(s.lastIndexOf('/') + 1).trim();
        return s.length() > 200 ? s.substring(s.length() - 200) : s;
    }

    /** 저장용 확장자: 영문·숫자만, 10자 이내. 없으면 빈 문자열 */
    public static String safeExt(String name) {
        int dot = name == null ? -1 : name.lastIndexOf('.');
        if (dot < 0 || dot == name.length() - 1) return "";
        String ext = name.substring(dot + 1).toLowerCase().replaceAll("[^a-z0-9]", "");
        return (ext.isEmpty() || ext.length() > 10) ? "" : "." + ext;
    }

    public static String hex(byte[] digest) {
        return HexFormat.of().formatHex(digest);
    }

    public static String sha256(byte[] data) {
        try {
            return hex(MessageDigest.getInstance("SHA-256").digest(data));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    public static String size(long bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return String.format("%.1f KB", bytes / 1024.0);
        return String.format("%.1f MB", bytes / 1024.0 / 1024.0);
    }

    public static int toInt(String s, int def) {
        try { return Integer.parseInt(s); } catch (Exception e) { return def; }
    }
}
