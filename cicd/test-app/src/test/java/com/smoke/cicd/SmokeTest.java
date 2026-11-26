package com.smoke.cicd;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.Test;
import static org.junit.Assert.assertTrue;

public class SmokeTest {
    @Test
    public void testPageContainsSmokeMarker() throws Exception {
        String html = Files.readString(Path.of("src/main/webapp/index.html"));
        assertTrue(html.contains("SMOKE CI/CD Test"));
        assertTrue(html.contains("id=\"version\""));
    }
}
