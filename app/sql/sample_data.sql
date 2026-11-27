-- =====================================================================
--  예시 데이터: 미리보기 사이트에 보이는 공지 12건 + 문의 2건
--  사용:  mysql -u root -p boarddb < sql/sample_data.sql   (schema.sql 먼저 실행)
--  게시글이 하나도 없을 때만 들어가요. 다시 넣으려면 아래 TRUNCATE 주석을 풀어요.
-- =====================================================================
USE boarddb;

-- TRUNCATE TABLE board_file; TRUNCATE TABLE board; TRUNCATE TABLE inquiry;

-- ---------------------------------------------------------------- 공지 12건
INSERT INTO board (title, writer, content, category, is_pinned, hit, reg_date)
SELECT * FROM (
    SELECT '홈페이지 리뉴얼 오픈' AS title, '운영팀' AS writer,
           '새로워진 홈페이지에서 공지와 자료를 더 편하게 확인하세요.' AS content,
           '공지' AS category, 0 AS is_pinned, 156 AS hit, NOW() - INTERVAL 52 DAY AS reg_date
    UNION ALL SELECT '백업 자동화 적용 및 복구 테스트 완료', '서버팀',
           '매일 새벽 cron 백업과 해시 리포트를 적용했고 복구 테스트를 마쳤습니다.',
           '점검', 0, 28, NOW() - INTERVAL 46 DAY
    UNION ALL SELECT '개인정보 처리방침 개정 안내', '관리팀',
           '개인정보 처리방침이 일부 개정되었습니다.',
           '공지', 0, 33, NOW() - INTERVAL 40 DAY
    UNION ALL SELECT '사내 메일 웹메일(Roundcube) 사용 설명서', '운영팀',
           '본사·지사 어디서나 HTTPS 웹메일로 접속하는 방법을 안내합니다.',
           '자료', 0, 115, NOW() - INTERVAL 33 DAY
    UNION ALL SELECT '첨부파일 저장소 S3 이관 일정', '클라우드팀',
           'NFS에 저장된 첨부파일을 S3로 이관합니다. 이관 중에도 내려받기는 정상 제공됩니다.',
           '공지', 0, 72, NOW() - INTERVAL 27 DAY
    UNION ALL SELECT 'SQL 인젝션 탐지 룰 업데이트 안내', '보안담당',
           'Snort 탐지 룰을 갱신했습니다. 탐지 시 운영 알림 메일로 즉시 통보됩니다.',
           '보안', 0, 58, NOW() - INTERVAL 23 DAY
    UNION ALL SELECT '블루그린 배포 전환 테스트 결과 공유', 'CI/CD',
           'Green 버전이 ALB 헬스체크를 통과한 뒤 트래픽을 전환했고, 전환 중 응답 오류는 없었습니다.\n실패 시에는 자동으로 Blue 버전으로 롤백됩니다.',
           '점검', 0, 39, NOW() - INTERVAL 18 DAY
    UNION ALL SELECT '운영 알림 메일(ops@) 수신 설정 방법', '운영팀',
           '보안 탐지, 백업 결과, 장애 알림은 운영 알림 메일함으로 발송됩니다.\nRoundcube 웹메일에서 필터를 설정해 알림을 분류해 보세요.',
           '자료', 0, 47, NOW() - INTERVAL 14 DAY
    UNION ALL SELECT '2026년 하반기 서비스 이용 가이드 (PDF)', '운영팀',
           '공지·자료실 이용 방법과 첨부파일 내려받기 안내 자료입니다.',
           '자료', 0, 203, NOW() - INTERVAL 10 DAY
    UNION ALL SELECT '외부 접속 시 VPN 사용 의무화 안내', '보안담당',
           '지사 및 재택 근무 시 사내 시스템 접속은 IPsec VPN을 통해서만 가능합니다.\n관리 서버(SSH) 직접 접속은 차단되며, 웹메일은 HTTPS로 이용하실 수 있습니다.',
           '보안', 0, 91, NOW() - INTERVAL 6 DAY
    UNION ALL SELECT '정기 보안 점검 일정 안내 (매월 둘째 주 토요일)', '보안담당',
           '매월 둘째 주 토요일 02:00 ~ 04:00 사이 방화벽 정책과 IDS 룰을 점검합니다.\n점검 중에도 공지·자료실은 정상적으로 이용하실 수 있습니다.',
           '점검', 0, 64, NOW() - INTERVAL 3 DAY
    UNION ALL SELECT '홈페이지 서비스 클라우드 이전 완료 안내', '운영팀',
           '공지·자료실 서비스가 AWS 서울 리전으로 이전되었습니다.\n\n이전 전후로 게시글 건수와 첨부파일 해시(SHA-256)를 비교해 모든 자료가 그대로 옮겨졌음을 확인했습니다.\n앞으로는 새 버전을 배포하는 동안에도 공지와 자료를 끊김 없이 이용하실 수 있습니다.',
           '공지', 1, 128, NOW() - INTERVAL 1 DAY
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM board);

-- ---------------------------------------------------------------- 첨부파일 메타데이터
-- (예시 첨부는 넣지 않음: 실제 파일이 없으면 다운로드 404 · 해시 NULL 이 되어 이관 대조를 흐림)

-- ---------------------------------------------------------------- 문의 예시 2건
INSERT INTO inquiry (company, name, email, phone, topic, message, status, reg_date)
SELECT * FROM (
    SELECT '예시상사' AS company, '김담당' AS name, 'manager@example.com' AS email, '010-0000-0000' AS phone,
           '클라우드 이전' AS topic, '사내 서버 한 대로 홈페이지를 운영 중입니다. AWS 이전 상담을 받고 싶습니다.' AS message,
           '접수' AS status, NOW() - INTERVAL 2 DAY AS reg_date
    UNION ALL SELECT '샘플물산', '박팀장', 'team@example.com', '',
           '보안 네트워크', '지사 VPN 구성과 방화벽 이중화 견적을 요청드립니다.',
           '회신 완료', NOW() - INTERVAL 5 DAY
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM inquiry);

-- ---------------------------------------------------------------- 확인
SELECT category, COUNT(*) AS cnt FROM board GROUP BY category;
SELECT COUNT(*) AS files FROM board_file;
SELECT COUNT(*) AS inquiries FROM inquiry;
