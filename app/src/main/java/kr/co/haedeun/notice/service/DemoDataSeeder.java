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
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 시연용 샘플 공지. APP_SEED=true 이고 공지 테이블이 비어 있을 때만 넣는다.
 * 운영(이관 대상 RDS)에서는 APP_SEED=false — 원본 데이터 건수 대조(NFR-03)가 틀어지지 않게 한다.
 */
@Component
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
        LocalDateTime now = LocalDateTime.now();

        add(Category.NOTICE, true, now.minusDays(2), "경영지원팀",
            "설 연휴 출하·고객지원 운영 일정 안내",
            """
            설 연휴 기간 출하와 고객지원 일정을 안내드립니다.

            - 마지막 출하: 연휴 시작 전날 15시 출고분까지
            - 연휴 중 긴급 품질 문의: 품질보증팀 당직 메일로 접수 (평일 기준 다음 영업일 회신)
            - 연휴 후 첫 출하: 연휴 종료 다음 날 오전 정상 출고

            납기가 걸린 발주는 영업 담당자와 미리 일정을 맞춰 주십시오.
            """, null, null);

        add(Category.QUALITY, true, now.minusDays(5), "품질보증팀",
            "IATF 16949 인증 갱신 심사 완료 및 인증서 게시",
            """
            본사 공장의 IATF 16949 갱신 심사가 부적합 사항 없이 완료되었습니다.
            고객사 협력업체 등록 서류에 첨부할 수 있도록 인증서 사본을 게시합니다.

            인증서 원본 대조가 필요하면 품질보증팀으로 요청해 주십시오.
            """, "IATF16949_인증서_사본_안내.txt",
            "해든정밀㈜ IATF 16949 인증서 사본 (시연용 샘플 파일)\n인증 범위: 정밀 가공 샤프트·하우징 부품의 제조\n");

        add(Category.DELIVERY, false, now.minusDays(8), "물류팀",
            "화성 2공장 출하장 이전에 따른 입차 경로 변경",
            """
            화성 2공장 출하장이 B동 후면으로 이전됩니다.
            납품 차량은 정문이 아니라 후문(물류 전용 게이트)으로 입차해 주십시오.

            - 적용: 다음 달 첫 영업일부터
            - 입차 가능 시간: 평일 08:00–17:00
            - 하차 대기: B동 후면 대기선(4대)
            """, "2공장_입차경로_안내.txt", "2공장 물류 게이트 → B동 후면 출하장 (시연용 샘플)\n");

        add(Category.ARCHIVE, false, now.minusDays(12), "기술영업팀",
            "2026 정밀 샤프트 제품 카탈로그 (Rev.C)",
            """
            샤프트 전 품목의 공차 등급, 표면 처리, 최소 발주 수량을 정리한 카탈로그입니다.
            Rev.B 대비 변경점: HS-2400 시리즈 추가, 열처리 사양 표기 통일.
            """, "HS_샤프트_카탈로그_RevC.csv",
            "품번,외경(mm),공차,표면처리,MOQ\nHS-2410,10,h6,무전해니켈,500\nHS-2420,20,h6,흑색산화,300\nHS-2440,40,g6,경질크롬,200\n");

        add(Category.ARCHIVE, false, now.minusDays(20), "환경안전팀",
            "절삭유 MSDS 개정판 게시",
            """
            공급사 변경에 따라 가공 라인 절삭유의 물질안전보건자료(MSDS)를 개정해 게시합니다.
            협력사 작업자 교육 자료로 사용해 주십시오.
            """, "절삭유_MSDS_개정판.txt", "MSDS 개정 요약 (시연용 샘플)\n- 취급 시 보호장갑 착용\n- 환기 설비 가동 중 사용\n");

        add(Category.QUALITY, false, now.minusDays(27), "품질보증팀",
            "4분기 협력사 품질 평가 결과 회신 일정",
            """
            4분기 협력사 품질 평가 결과를 다음 주 금요일까지 개별 메일로 회신합니다.
            평가 항목: 납입 불량률(PPM), 시정조치 회신 기한 준수율, 변경점 사전 신고 여부.
            """, null, null);

        add(Category.NOTICE, false, now.minusDays(35), "경영지원팀",
            "고객 공지·자료실 서비스 이전 안내",
            """
            공지·자료실을 새 서비스 환경으로 이전합니다.
            주소는 바뀌지 않으며, 기존 게시글과 첨부파일은 그대로 옮겨집니다.

            이전 작업 중 짧은 시간 동안 글 등록과 파일 업로드만 일시 중지되며, 공지 조회와 다운로드는 계속 가능합니다.
            """, null, null);

        log.info("시연용 공지 {}건을 넣었습니다 (APP_SEED=true).", notices.count());
    }

    private void add(Category c, boolean pinned, LocalDateTime at, String author, String title, String body,
                     String fileName, String fileBody) throws IOException {
        Notice n = new Notice(c, title, body.strip(), author, pinned, false);
        n.backdate(at);
        if (fileName != null) {
            byte[] bytes = fileBody.getBytes(StandardCharsets.UTF_8);
            StorageService.Stored s = storage.save(new ByteArrayInputStream(bytes), bytes.length);
            String type = fileName.endsWith(".csv") ? "text/csv" : "text/plain";
            n.addAttachment(new Attachment(fileName, s.storedName(), type, s.size(), s.sha256()));
        }
        notices.save(n);
    }
}
