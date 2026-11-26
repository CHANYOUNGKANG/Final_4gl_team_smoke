package kr.co.haedeun.notice.service;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import kr.co.haedeun.notice.config.AppProperties;
import kr.co.haedeun.notice.domain.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 로컬(H2) 시연용 샘플. 글 8건은 server/db/smoke_board.sql 의 샘플과 같다.
 * 로컬에서는 자료실이 비지 않도록 첨부 샘플 파일 몇 개를 더 붙인다.
 * APP_SEED=true 이고 notice 테이블이 비어 있을 때만 넣는다. 운영(prod)은 APP_SEED=false.
 */
@Component
@Order(2)
public class DemoDataSeeder implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DemoDataSeeder.class);

    private final AppProperties props;
    private final NoticeRepository notices;
    private final StorageService storage;

    public DemoDataSeeder(AppProperties props, NoticeRepository notices, StorageService storage) {
        this.props = props;
        this.notices = notices;
        this.storage = storage;
    }

    @Override
    @Transactional
    public void run(ApplicationArguments args) throws IOException {
        if (!props.seed() || notices.count() > 0) return;

        add(Category.NOTICE, "공지·자료실 이용 안내",
            "해든정밀㈜ 고객사·협력사 전용 공지·자료실입니다. 납품 일정, 품질 인증서, 도면은 각 분류에서 확인해 주세요.",
            "관리자", true, "2026-11-02T09:00:00", null, null);
        add(Category.NOTICE, "시스템 점검 안내 (12/06 02:00~04:00)",
            "서비스 이전 작업으로 12월 6일 02:00부터 04:00까지 자료 업로드가 중지됩니다. 조회는 계속 가능합니다.",
            "관리자", true, "2026-11-20T10:30:00", null, null);
        add(Category.DELIVERY, "12월 1주차 납품 일정",
            "A-1024 샤프트 400EA 12/02 출고, B-207 플랜지 150EA 12/04 출고 예정입니다.",
            "생산관리팀", false, "2026-11-24T14:00:00", "12월1주차_납품일정.csv",
            "품번,품명,수량,출고일\nA-1024,샤프트,400,12/02\nB-207,플랜지,150,12/04\n");
        add(Category.DELIVERY, "연말 출하 마감 일정 안내",
            "12월 마지막 출하는 12/26(금)입니다. 추가 발주는 12/19까지 요청해 주세요.",
            "생산관리팀", false, "2026-11-25T11:20:00", null, null);
        add(Category.QUALITY, "ISO 9001 인증서 갱신본 게시",
            "2026년 ISO 9001 갱신 인증서를 첨부합니다. 협력사 등록 서류로 사용하실 수 있습니다.",
            "품질보증팀", false, "2026-11-10T16:45:00", "ISO9001_인증서_2026.txt",
            "해든정밀㈜ ISO 9001 인증서 사본 (시연용 샘플 파일)\n");
        add(Category.QUALITY, "A-1024 샤프트 성적서 (LOT 2611-03)",
            "치수 검사와 경도 시험 결과입니다. 측정 장비 교정 기록을 함께 첨부합니다.",
            "품질보증팀", false, "2026-11-21T13:10:00", "A-1024_성적서_LOT2611-03.csv",
            "항목,규격,측정값,판정\n외경(mm),20.000±0.013,20.004,합격\n경도(HRC),58~62,60,합격\n");
        add(Category.DRAWING, "B-207 플랜지 도면 Rev.C",
            "볼트 구멍 위치 변경이 반영된 Rev.C 도면입니다. Rev.B 는 더 이상 사용하지 마세요.",
            "설계팀", false, "2026-11-18T09:40:00", "B-207_플랜지_RevC_도면안내.txt",
            "B-207 플랜지 Rev.C — 볼트 구멍 PCD 변경 (시연용 샘플 파일)\n");
        add(Category.DRAWING, "C-55 브래킷 신규 도면",
            "신규 부품 C-55 브래킷 도면입니다. 시제품 검토 의견은 메일로 보내 주세요.",
            "설계팀", false, "2026-11-23T15:05:00", null, null);

        log.info("시연용 공지 {}건을 넣었습니다 (APP_SEED=true).", notices.count());
    }

    private void add(Category c, String title, String body, String writer, boolean pinned, String at,
                     String fileName, String fileBody) throws IOException {
        Notice n = new Notice(c, title, body, writer, pinned, false);
        n.backdate(LocalDateTime.parse(at));
        if (fileName != null) {
            byte[] bytes = fileBody.getBytes(StandardCharsets.UTF_8);
            StorageService.Stored s = storage.save(new ByteArrayInputStream(bytes), bytes.length, fileName);
            String type = fileName.endsWith(".csv") ? "text/csv" : "text/plain";
            n.addAttachment(new Attachment(fileName, s.storedName(), type, s.size(), s.sha256()));
        }
        notices.save(n);
    }
}
