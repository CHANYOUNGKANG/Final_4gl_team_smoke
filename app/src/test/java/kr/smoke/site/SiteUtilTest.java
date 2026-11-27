package kr.smoke.site;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class SiteUtilTest {

    @Test
    void shortCommitTakesSevenChars() {
        assertEquals("abc1234", SiteUtil.shortCommit("abc1234def5678"));
        assertEquals("abc", SiteUtil.shortCommit(" abc "));
        assertEquals("", SiteUtil.shortCommit(null));
    }

    @Test
    void tokenMustMatchExactlyAndNotBeEmpty() {
        assertTrue(SiteUtil.tokenMatches("s3cret-token-value", "s3cret-token-value"));
        assertFalse(SiteUtil.tokenMatches("s3cret-token-value", "s3cret-token-valuE"));
        assertFalse(SiteUtil.tokenMatches("s3cret-token-value", null));
        assertFalse(SiteUtil.tokenMatches("", ""));
        assertFalse(SiteUtil.tokenMatches(null, "x"));
    }

    @Test
    void jsonObjectEscapesAndNests() {
        Map<String, Object> served = new LinkedHashMap<>();
        served.put("version", "v1");
        served.put("color", "blue");
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", 7);
        m.put("title", "제목 \"따옴표\"\n<b>");
        m.put("servedBy", served);
        assertEquals("{\"id\":7,\"title\":\"제목 \\\"따옴표\\\"\\n\\u003cb\\u003e\",\"servedBy\":{\"version\":\"v1\",\"color\":\"blue\"}}",
                SiteUtil.jsonObject(m));
    }

    @Test
    void jsonFieldReadsCheckRequest() {
        String body = "{ \"title\" : \"ci-check\", \"content\":\"줄1\\n줄2 \\\"q\\\" \\u0041\" }";
        assertEquals("ci-check", SiteUtil.jsonField(body, "title"));
        assertEquals("줄1\n줄2 \"q\" A", SiteUtil.jsonField(body, "content"));
        assertNull(SiteUtil.jsonField(body, "missing"));
        assertNull(SiteUtil.jsonField("{\"title\":5}", "title"));
        assertNull(SiteUtil.jsonField("not json", "title"));
        assertNull(SiteUtil.jsonField("{\"title\":\"unterminated", "title"));
    }

    @Test
    void sha256HexMatchesKnownVector() {
        byte[] d = SiteUtil.sha256().digest("abc".getBytes(StandardCharsets.UTF_8));
        assertEquals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", SiteUtil.hex(d));
    }

    @Test
    void mailHeaderInjectionIsBlocked() {
        String evil = "a@b.com\r\nBcc: x@y.com";
        assertEquals("a@b.com Bcc: x@y.com", SiteUtil.oneLine(evil));
        assertFalse(SiteUtil.isAsciiAddress(SiteUtil.oneLine(evil)));
        assertTrue(SiteUtil.isAsciiAddress("smoke@smoke.local"));
        assertFalse(SiteUtil.isAsciiAddress("<a@b>"));
    }

    @Test
    void checkApiIdParsesPath() {
        assertEquals(0, SiteUtil.checkApiId("/api/check/notices", ""));
        assertEquals(0, SiteUtil.checkApiId("/ctx/api/check/notices/", "/ctx"));
        assertEquals(42, SiteUtil.checkApiId("/api/check/notices/42", ""));
        assertEquals(-1, SiteUtil.checkApiId("/api/check/notices/4x", ""));
        assertEquals(-1, SiteUtil.checkApiId("/api/check/notices/1/2", ""));
        assertEquals(-1, SiteUtil.checkApiId("/other", ""));
    }
}
