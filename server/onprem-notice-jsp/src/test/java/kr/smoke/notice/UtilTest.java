package kr.smoke.notice;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;

class UtilTest {

    @Test
    void escapesHtml() {
        assertEquals("&lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt;", Util.esc("<script>alert('x')</script>"));
        assertEquals("", Util.esc(null));
    }

    @Test
    void escapesJson() {
        assertEquals("\"a\\\"b\\n\\u003cx\\u003e\"", Util.json("a\"b\n<x>"));
        assertEquals("null", Util.json(null));
    }

    @Test
    void categoriesMatchDbConstraint() {
        assertTrue(Util.validCategory("도면"));
        assertFalse(Util.validCategory("기타"));
        assertFalse(Util.validCategory(null));
    }

    @Test
    void stripsPathFromUploadName() {
        assertEquals("b.pdf", Util.baseName("C:\\Users\\a\\b.pdf"));
        assertEquals("passwd", Util.baseName("../../etc/passwd"));
    }

    @Test
    void keepsOnlySafeExtension() {
        assertEquals(".pdf", Util.safeExt("도면 Rev.C.PDF"));
        assertEquals("", Util.safeExt("noext"));
        assertEquals(".jsp", Util.safeExt("x.j$sp"));
    }

    @Test
    void sha256KnownValue() {
        assertEquals("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                Util.sha256(new byte[0]));
        assertEquals(64, Util.sha256("공지".getBytes(StandardCharsets.UTF_8)).length());
    }
}
