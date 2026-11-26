package kr.co.haedeun.notice.web;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.io.IOException;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import kr.co.haedeun.notice.config.AppProperties;
import kr.co.haedeun.notice.domain.Category;
import kr.co.haedeun.notice.domain.Notice;
import kr.co.haedeun.notice.service.NoticeService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 배포 검증 API (CICD3·4 "공지 작성·조회 검사").
 * Jenkins 가 Credentials 의 CHECK_TOKEN 을 X-Check-Token 헤더로 보낸다. 토큰이 설정되지 않으면 API 전체가 404.
 * 검증 글은 is_check=1 로 저장돼(이관 건수 v_migration_check 에서도 빠진다) 고객 화면에는 보이지 않고, 검사 끝에 DELETE 로 지운다.
 */
@RestController
@RequestMapping("/api/check/notices")
public class CheckApiController {

    public record CheckRequest(@NotBlank @Size(max = 200) String title, @NotBlank @Size(max = 2000) String content) {}

    private final AppProperties props;
    private final NoticeService service;

    public CheckApiController(AppProperties props, NoticeService service) {
        this.props = props;
        this.service = service;
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> create(@RequestHeader(value = "X-Check-Token", required = false) String token,
                                                      @Valid @RequestBody CheckRequest req) throws IOException {
        guard(token);
        Notice n = service.create(Category.NOTICE, req.title(), req.content(), "deploy-check", false, true, List.of());
        return ResponseEntity.created(URI.create("/api/check/notices/" + n.getId())).body(view(n));
    }

    @GetMapping("/{id}")
    public Map<String, Object> read(@RequestHeader(value = "X-Check-Token", required = false) String token,
                                    @PathVariable int id) {
        guard(token);
        return view(service.readForCheck(id));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@RequestHeader(value = "X-Check-Token", required = false) String token,
                                       @PathVariable int id) {
        guard(token);
        Notice n = service.readForCheck(id);
        if (!n.isCheckPost()) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build(); // 고객 공지는 검증 API로 지우지 않는다
        }
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    private void guard(String token) {
        if (!props.checkApiEnabled()) {
            throw new org.springframework.web.server.ResponseStatusException(HttpStatus.NOT_FOUND);
        }
        boolean ok = token != null && MessageDigest.isEqual(
                token.getBytes(StandardCharsets.UTF_8), props.checkToken().getBytes(StandardCharsets.UTF_8));
        if (!ok) {
            throw new org.springframework.web.server.ResponseStatusException(HttpStatus.UNAUTHORIZED);
        }
    }

    private Map<String, Object> view(Notice n) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", n.getId());
        m.put("docNo", n.getDocNo());
        m.put("title", n.getTitle());
        m.put("content", n.getContent());
        m.put("servedBy", Map.of("version", props.version(), "color", props.slot(), "commit", props.shortCommit()));
        return m;
    }
}
