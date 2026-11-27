package kr.smoke.site;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Map;

/**
 * JSP 에서 같이 쓰는 순수 함수 모음 (서블릿·DB 없이 단위 테스트 가능).
 * JSON 응답 · 검증 API 토큰 비교 · 커밋 표시 · 해시 · 메일 헤더 정리.
 */
public final class SiteUtil {

    /** CI/CD 규격: /health · /version 의 app 값 */
    public static final String APP_NAME = "haedeun-notice";

    private SiteUtil() {}

    /** GIT_COMMIT 앞 7자리 (없으면 빈 문자열) */
    public static String shortCommit(String commit) {
        if (commit == null) return "";
        String c = commit.trim();
        return c.length() > 7 ? c.substring(0, 7) : c;
    }

    /** 길이와 무관하게 같은 시간에 비교 (토큰이 비었거나 null 이면 false) */
    public static boolean tokenMatches(String expected, String given) {
        if (expected == null || expected.isEmpty() || given == null) return false;
        return MessageDigest.isEqual(expected.getBytes(StandardCharsets.UTF_8), given.getBytes(StandardCharsets.UTF_8));
    }

    /** JSON 문자열 값 이스케이프 (따옴표 포함해서 돌려줌) */
    public static String jsonString(String s) {
        if (s == null) return "null";
        StringBuilder b = new StringBuilder(s.length() + 16).append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':  b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                case '<':  b.append("\\u003c"); break;   // HTML 안에 끼어도 안전하게
                case '>':  b.append("\\u003e"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
            }
        }
        return b.append('"').toString();
    }

    /** 값이 문자열·숫자·불린·중첩 맵인 단순 JSON 객체 */
    public static String jsonObject(Map<String, ?> m) {
        StringBuilder b = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, ?> e : m.entrySet()) {
            if (!first) b.append(',');
            first = false;
            b.append(jsonString(e.getKey())).append(':');
            Object v = e.getValue();
            if (v == null) b.append("null");
            else if (v instanceof Number || v instanceof Boolean) b.append(v);
            else if (v instanceof Map) {
                @SuppressWarnings("unchecked") Map<String, ?> mm = (Map<String, ?>) v;
                b.append(jsonObject(mm));
            } else b.append(jsonString(String.valueOf(v)));
        }
        return b.append('}').toString();
    }

    /**
     * 평평한 JSON 객체에서 문자열 필드 하나를 꺼냄. 없거나 문자열이 아니면 null.
     * 검증 API 요청 {"title":"…","content":"…"} 정도만 다루는 최소 파서.
     */
    public static String jsonField(String json, String field) {
        if (json == null) return null;
        int i = 0, n = json.length();
        while (i < n) {
            int k = json.indexOf('"', i);
            if (k < 0) return null;
            int[] end = new int[1];
            String key = readString(json, k, end);
            if (key == null) return null;
            int j = end[0];
            while (j < n && Character.isWhitespace(json.charAt(j))) j++;
            if (j < n && json.charAt(j) == ':') {
                j++;
                while (j < n && Character.isWhitespace(json.charAt(j))) j++;
                if (j < n && json.charAt(j) == '"') {
                    String val = readString(json, j, end);
                    if (val == null) return null;
                    if (key.equals(field)) return val;
                    i = end[0];
                    continue;
                }
                if (key.equals(field)) return null;
            }
            i = j;
        }
        return null;
    }

    private static String readString(String s, int quote, int[] end) {
        StringBuilder b = new StringBuilder();
        int i = quote + 1;
        while (i < s.length()) {
            char c = s.charAt(i);
            if (c == '"') { end[0] = i + 1; return b.toString(); }
            if (c == '\\') {
                if (i + 1 >= s.length()) return null;
                char e = s.charAt(++i);
                switch (e) {
                    case 'n': b.append('\n'); break;
                    case 'r': b.append('\r'); break;
                    case 't': b.append('\t'); break;
                    case 'b': b.append('\b'); break;
                    case 'f': b.append('\f'); break;
                    case 'u':
                        if (i + 4 >= s.length()) return null;
                        try { b.append((char) Integer.parseInt(s.substring(i + 1, i + 5), 16)); }
                        catch (NumberFormatException ex) { return null; }
                        i += 4;
                        break;
                    default: b.append(e);
                }
            } else b.append(c);
            i++;
        }
        return null;
    }

    /** 바이트 → 소문자 16진수 */
    public static String hex(byte[] d) {
        StringBuilder b = new StringBuilder(d.length * 2);
        for (byte x : d) b.append(String.format("%02x", x));
        return b.toString();
    }

    public static MessageDigest sha256() {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }

    /** 메일 헤더에 줄바꿈이 끼어들지 못하게 한 줄로 정리 (헤더 주입 방지) */
    public static String oneLine(String s) {
        return s == null ? "" : s.replaceAll("[\\r\\n]+", " ").trim();
    }

    /** SMTP 주소로 써도 되는 ASCII 메일 주소인지 */
    public static boolean isAsciiAddress(String s) {
        return s != null && s.matches("^[\\x21-\\x7E&&[^<>]]+@[\\x21-\\x7E&&[^<>]]+$");
    }

    /** /api/check/notices/{id} 에서 id 를 꺼냄. 형식이 아니면 -1, id 없이 목록 주소면 0 */
    public static int checkApiId(String uri, String contextPath) {
        if (uri == null) return -1;
        String p = uri.substring(contextPath == null ? 0 : contextPath.length());
        String base = "/api/check/notices";
        if (p.equals(base) || p.equals(base + "/")) return 0;
        if (!p.startsWith(base + "/")) return -1;
        String rest = p.substring(base.length() + 1);
        if (!rest.matches("\\d{1,9}")) return -1;
        return Integer.parseInt(rest);
    }

    /** /notices/{id} 의 pathInfo("/12") 에서 id. 비었으면 0, 형식이 아니면 -1 */
    public static int noticeId(String pathInfo) {
        if (pathInfo == null || pathInfo.isEmpty() || "/".equals(pathInfo)) return 0;
        String rest = pathInfo.substring(1);
        if (!rest.matches("[1-9]\\d{0,8}")) return -1;
        return Integer.parseInt(rest);
    }
}
