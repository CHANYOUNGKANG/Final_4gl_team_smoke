-- =====================================================================
-- smoke_board : 해든정밀㈜ 공지·자료실 DB
-- 대상: data 서버 (10.10.40.10) MariaDB 10.11
-- 팀 기준: utf8mb4 / utf8mb4_unicode_ci (README 기준안과 동일)
-- 실행:  sudo mysql -u root -p < smoke_board.sql
-- 주의: 기존 smoke_board 의 테이블을 지우고 새로 만든다 (처음 구축용)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS smoke_board
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
ALTER DATABASE smoke_board
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smoke_board;

DROP VIEW  IF EXISTS v_migration_check;
DROP TABLE IF EXISTS attachment;
DROP TABLE IF EXISTS notice;
DROP TABLE IF EXISTS admin_user;

-- ---------------------------------------------------------------------
-- 1. 관리자 (공지 작성·수정 권한)
--    비밀번호는 앱에서 bcrypt 등으로 해시해서 넣는다. 평문 저장 금지.
-- ---------------------------------------------------------------------
CREATE TABLE admin_user (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(50)  NOT NULL,
  password_hash VARCHAR(100) NOT NULL COMMENT '해시값만 저장',
  display_name  VARCHAR(50)  NOT NULL,
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 2. 공지·자료실 게시글
--    category : 공지 / 납품일정 / 품질인증 / 도면
--    is_check : Jenkins Green 검사가 쓰는 "검증 공지" 표시.
--               1 이면 목록과 이관 건수에서 뺀다.
-- ---------------------------------------------------------------------
CREATE TABLE notice (
  notice_id   INT AUTO_INCREMENT PRIMARY KEY,
  category    VARCHAR(20)  NOT NULL DEFAULT '공지',
  title       VARCHAR(200) NOT NULL,
  content     TEXT         NOT NULL,
  writer      VARCHAR(50)  NOT NULL,
  is_pinned   TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '상단 고정',
  is_check    TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '배포 검증용 글',
  view_count  INT          NOT NULL DEFAULT 0,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME     NULL ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT ck_category CHECK (category IN ('공지','납품일정','품질인증','도면')),
  KEY idx_list (is_check, is_pinned, created_at),
  KEY idx_category (category, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 3. 첨부파일
--    실제 파일은 NFS(/share/attach) → 이관 후 S3 에 stored_name 으로 저장.
--    저장 폴더 경로는 DB에 넣지 않고 앱 설정(UPLOAD_DIR)으로 둔다.
--    → S3 로 옮겨도 DB는 그대로, 설정만 바꾸면 된다.
--    sha256 은 업로드 때 계산해 저장 → 이관 전후 대조 기준.
-- ---------------------------------------------------------------------
CREATE TABLE attachment (
  file_id     INT AUTO_INCREMENT PRIMARY KEY,
  notice_id   INT          NOT NULL,
  orig_name   VARCHAR(255) NOT NULL COMMENT '사용자가 올린 파일 이름',
  stored_name VARCHAR(100) NOT NULL COMMENT '저장 이름 (UUID.확장자)',
  file_size   BIGINT       NOT NULL,
  mime_type   VARCHAR(100) NULL,
  sha256      CHAR(64)     NOT NULL,
  uploaded_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_stored (stored_name),
  KEY idx_notice (notice_id),
  CONSTRAINT fk_attach_notice FOREIGN KEY (notice_id)
    REFERENCES notice (notice_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 4. 샘플 게시글 (해든정밀 시나리오)
-- ---------------------------------------------------------------------
INSERT INTO notice (category, title, content, writer, is_pinned, created_at) VALUES
('공지',     '공지·자료실 이용 안내',
 '해든정밀㈜ 고객사·협력사 전용 공지·자료실입니다. 납품 일정, 품질 인증서, 도면은 각 분류에서 확인해 주세요.',
 '관리자', 1, '2026-11-02 09:00:00'),
('공지',     '시스템 점검 안내 (12/06 02:00~04:00)',
 '서비스 이전 작업으로 12월 6일 02:00부터 04:00까지 자료 업로드가 중지됩니다. 조회는 계속 가능합니다.',
 '관리자', 1, '2026-11-20 10:30:00'),
('납품일정', '12월 1주차 납품 일정',
 'A-1024 샤프트 400EA 12/02 출고, B-207 플랜지 150EA 12/04 출고 예정입니다.',
 '생산관리팀', 0, '2026-11-24 14:00:00'),
('납품일정', '연말 출하 마감 일정 안내',
 '12월 마지막 출하는 12/26(금)입니다. 추가 발주는 12/19까지 요청해 주세요.',
 '생산관리팀', 0, '2026-11-25 11:20:00'),
('품질인증', 'ISO 9001 인증서 갱신본 게시',
 '2026년 ISO 9001 갱신 인증서를 첨부합니다. 협력사 등록 서류로 사용하실 수 있습니다.',
 '품질보증팀', 0, '2026-11-10 16:45:00'),
('품질인증', 'A-1024 샤프트 성적서 (LOT 2611-03)',
 '치수 검사와 경도 시험 결과입니다. 측정 장비 교정 기록을 함께 첨부합니다.',
 '품질보증팀', 0, '2026-11-21 13:10:00'),
('도면',     'B-207 플랜지 도면 Rev.C',
 '볼트 구멍 위치 변경이 반영된 Rev.C 도면입니다. Rev.B 는 더 이상 사용하지 마세요.',
 '설계팀', 0, '2026-11-18 09:40:00'),
('도면',     'C-55 브래킷 신규 도면',
 '신규 부품 C-55 브래킷 도면입니다. 시제품 검토 의견은 메일로 보내 주세요.',
 '설계팀', 0, '2026-11-23 15:05:00');

-- ---------------------------------------------------------------------
-- 5. 이관 대조용 뷰 (온프레미스와 RDS 에서 같은 결과가 나와야 한다)
--    notice_count  : 게시글 건수 (검증 글 제외)
--    file_count    : 첨부파일 수
--    content_digest: 모든 글 본문 해시를 이어 붙여 다시 해시한 값
--    file_digest   : 모든 첨부 sha256 을 이어 붙여 다시 해시한 값
-- ---------------------------------------------------------------------
CREATE VIEW v_migration_check AS
SELECT
  (SELECT COUNT(*) FROM notice WHERE is_check = 0) AS notice_count,
  (SELECT COUNT(*) FROM attachment a
     JOIN notice n ON n.notice_id = a.notice_id
    WHERE n.is_check = 0)                          AS file_count,
  (SELECT SHA2(GROUP_CONCAT(CONCAT(notice_id, ':', SHA2(content, 256))
                ORDER BY notice_id SEPARATOR ','), 256)
     FROM notice WHERE is_check = 0)               AS content_digest,
  (SELECT SHA2(GROUP_CONCAT(CONCAT(a.file_id, ':', a.sha256)
                ORDER BY a.file_id SEPARATOR ','), 256)
     FROM attachment a
     JOIN notice n ON n.notice_id = a.notice_id
    WHERE n.is_check = 0)                          AS file_digest;

-- ---------------------------------------------------------------------
-- 6. 앱 계정 (web 서버에서만 접속, 필요한 권한만)
--    '비밀번호' 는 직접 정한 값으로 바꿔서 실행한다.
--    192.168.111.% 는 NAT 로 작업하는 동안만 쓰는 임시 계정 → 연동 후 DROP USER
-- ---------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'smoke'@'10.10.30.%'    IDENTIFIED BY '비밀번호';
CREATE USER IF NOT EXISTS 'smoke'@'192.168.111.%' IDENTIFIED BY '비밀번호';
GRANT SELECT, INSERT, UPDATE, DELETE ON smoke_board.* TO 'smoke'@'10.10.30.%';
GRANT SELECT, INSERT, UPDATE, DELETE ON smoke_board.* TO 'smoke'@'192.168.111.%';
FLUSH PRIVILEGES;

-- 확인
SELECT category, COUNT(*) AS cnt FROM notice GROUP BY category;
SELECT * FROM v_migration_check;
