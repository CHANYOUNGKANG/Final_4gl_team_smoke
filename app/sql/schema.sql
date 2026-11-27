-- =====================================================================
--  ㈜스모크 회사 사이트 · 공지/자료실 DB  (MariaDB 10.11 / RDS MariaDB)
--  사용:  sudo mysql < schema.sql           (예시 글: sample_data.sql)
--  여러 번 실행해도 안전 (IF NOT EXISTS) · 기존 글 보존
--  계정 비밀번호는 저장소에 두지 않는다 → 아래 '비밀번호' 자리를 실행할 때만 바꿔 넣는다
-- =====================================================================
CREATE DATABASE IF NOT EXISTS boarddb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE boarddb;

-- 1) 게시글 · is_check=1 은 배포 검증 API 가 만든 글 (공개 화면·이관 대조에서 제외)
CREATE TABLE IF NOT EXISTS board (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    title     VARCHAR(200) NOT NULL,
    writer    VARCHAR(50)  NOT NULL,
    content   TEXT,
    reg_date  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
ALTER TABLE board ADD COLUMN IF NOT EXISTS category  VARCHAR(20) NOT NULL DEFAULT '공지';  -- 공지 · 자료 · 보안 · 점검
ALTER TABLE board ADD COLUMN IF NOT EXISTS hit       INT         NOT NULL DEFAULT 0;
ALTER TABLE board ADD COLUMN IF NOT EXISTS is_pinned TINYINT     NOT NULL DEFAULT 0;
ALTER TABLE board ADD COLUMN IF NOT EXISTS is_check  TINYINT     NOT NULL DEFAULT 0;

-- 2) 첨부 메타데이터 · 실제 파일은 APP_STORAGE_DIR (온프레미스 NFS → 이관 후 S3/EFS)
--    stored_name = YYYYMM/UUID.확장자 = S3 키 · sha256 은 업로드할 때 앱이 계산
CREATE TABLE IF NOT EXISTS board_file (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    board_id     INT          NOT NULL,
    orig_name    VARCHAR(255) NOT NULL,
    stored_name  VARCHAR(255) NOT NULL,
    file_size    BIGINT       NOT NULL DEFAULT 0,
    content_type VARCHAR(120),
    reg_date     DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE INDEX IF NOT EXISTS idx_board_file_board ON board_file (board_id);
ALTER TABLE board_file ADD COLUMN IF NOT EXISTS sha256 CHAR(64) NULL;

-- 3) 홈페이지 문의 접수 (MAIL_TO 설정 시 사내 메일로 알림)
CREATE TABLE IF NOT EXISTS inquiry (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    company   VARCHAR(100),
    name      VARCHAR(50)  NOT NULL,
    email     VARCHAR(120) NOT NULL,
    phone     VARCHAR(40),
    topic     VARCHAR(40),
    message   TEXT         NOT NULL,
    status    VARCHAR(20)  NOT NULL DEFAULT '접수',
    reg_date  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4) 이관 대조 뷰 · 온프레미스와 RDS 에서 같은 값이 나와야 이관 성공
--    조회수(hit)는 이관 중에도 바뀔 수 있어 제외, 검증 글(is_check=1)과 그 첨부도 제외
CREATE OR REPLACE VIEW v_migration_check AS
SELECT
  (SELECT COUNT(*) FROM board WHERE is_check = 0)                       AS notice_count,
  (SELECT COUNT(*) FROM board_file f JOIN board b ON b.id = f.board_id
     WHERE b.is_check = 0)                                              AS file_count,
  (SELECT COUNT(*) FROM inquiry)                                        AS inquiry_count,
  (SELECT SHA2(GROUP_CONCAT(CONCAT_WS('|', id, category, title, writer, content, is_pinned, reg_date)
                            ORDER BY id SEPARATOR '\n'), 256)
     FROM board WHERE is_check = 0)                                     AS content_digest,
  (SELECT SHA2(GROUP_CONCAT(CONCAT_WS('|', f.id, f.board_id, f.stored_name, f.file_size, IFNULL(f.sha256, '-'))
                            ORDER BY f.id SEPARATOR '\n'), 256)
     FROM board_file f JOIN board b ON b.id = f.board_id WHERE b.is_check = 0) AS file_digest;

-- 5) 앱 계정 (서비스망 web 서버 대역만) · 앱은 테이블을 만들 권한이 없어도 동작한다
--    CREATE USER IF NOT EXISTS 'boarduser'@'10.10.30.%' IDENTIFIED BY '비밀번호';
--    GRANT SELECT, INSERT, UPDATE, DELETE ON boarddb.* TO 'boarduser'@'10.10.30.%';
