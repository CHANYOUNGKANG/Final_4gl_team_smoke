package kr.co.haedeun.notice.config;

import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 모든 운영 값은 환경 변수로 주입한다 (README 팀 보안 규칙).
 * 비밀값(관리자 비밀번호, 검증 토큰, DB 비밀번호)은 Jenkins Credentials · Kubernetes Secret 에서만 넣는다.
 */
@ConfigurationProperties(prefix = "app")
public record AppProperties(
        String version,
        String commit,
        String color,
        String storageDir,
        long maxFileBytes,
        List<String> allowedExtensions,
        String checkToken,
        String adminUsername,
        String adminPassword,
        boolean seed) {

    public boolean checkApiEnabled() {
        return checkToken != null && checkToken.length() >= 16;
    }

    public boolean adminEnabled() {
        return adminPassword != null && !adminPassword.isBlank();
    }

    public String shortCommit() {
        if (commit == null || commit.isBlank()) return "local";
        return commit.length() > 7 ? commit.substring(0, 7) : commit;
    }

    /** blue | green | 그 외(로컬) */
    public String slot() {
        if (color == null) return "local";
        String c = color.trim().toLowerCase();
        return (c.equals("blue") || c.equals("green")) ? c : "local";
    }
}
