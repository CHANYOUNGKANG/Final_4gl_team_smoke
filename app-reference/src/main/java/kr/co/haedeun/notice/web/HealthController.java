package kr.co.haedeun.notice.web;

import java.util.LinkedHashMap;
import java.util.Map;
import kr.co.haedeun.notice.config.AppProperties;
import kr.co.haedeun.notice.service.NoticeService;
import kr.co.haedeun.notice.service.StorageService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * ALB 대상 그룹·Kubernetes readinessProbe·Jenkins 검증이 함께 쓰는 상태 검사.
 * DB 조회와 첨부 저장소 쓰기가 모두 되어야 200, 하나라도 안 되면 503.
 */
@RestController
public class HealthController {

    private final AppProperties props;
    private final NoticeService service;
    private final StorageService storage;

    public HealthController(AppProperties props, NoticeService service, StorageService storage) {
        this.props = props;
        this.service = service;
        this.storage = storage;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> body = new LinkedHashMap<>(version());
        String db;
        try {
            service.publicCount();
            db = "UP";
        } catch (RuntimeException e) {
            db = "DOWN";
        }
        String files = storage.writable() ? "UP" : "DOWN";
        boolean up = db.equals("UP") && files.equals("UP");
        body.put("status", up ? "UP" : "DOWN");
        body.put("db", db);
        body.put("storage", files);
        return ResponseEntity.status(up ? 200 : 503).body(body);
    }

    /** 배포 전환 확인용: 운영 주소가 지금 어느 버전·슬롯을 보고 있는지. */
    @GetMapping("/version")
    public Map<String, Object> version() {
        Map<String, Object> v = new LinkedHashMap<>();
        v.put("app", "haedeun-notice");
        v.put("version", props.version());
        v.put("commit", props.shortCommit());
        v.put("color", props.slot());
        return v;
    }
}
