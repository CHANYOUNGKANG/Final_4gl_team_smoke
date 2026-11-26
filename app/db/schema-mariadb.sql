-- 해든정밀 공지·자료실 스키마 (MariaDB 10.x / RDS for MariaDB)
-- 운영(prod 프로필)은 DB_DDL=validate 가 기본이므로, 첫 배포 전에 이 스키마를 먼저 만든다.
-- 온프레미스 데이터 서버의 원본 덤프를 RDS로 복원할 때도 이 구조를 기준으로 건수·해시를 대조한다.
CREATE TABLE IF NOT EXISTS notice (
  id          BIGINT       NOT NULL AUTO_INCREMENT,
  category    VARCHAR(20)  NOT NULL,
  title       VARCHAR(200) NOT NULL,
  content     TEXT         NOT NULL,
  author      VARCHAR(50)  NOT NULL,
  pinned      BIT(1)       NOT NULL,
  hidden      BIT(1)       NOT NULL,
  view_count  BIGINT       NOT NULL,
  created_at  DATETIME(6)  NOT NULL,
  PRIMARY KEY (id),
  KEY idx_notice_list (hidden, pinned, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS attachment (
  id             BIGINT       NOT NULL AUTO_INCREMENT,
  notice_id      BIGINT       NOT NULL,
  original_name  VARCHAR(255) NOT NULL,
  stored_name    VARCHAR(64)  NOT NULL,
  content_type   VARCHAR(100),
  size_bytes     BIGINT       NOT NULL,
  sha256         VARCHAR(64)  NOT NULL,
  download_count BIGINT       NOT NULL,
  created_at     DATETIME(6)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_attachment_stored (stored_name),
  KEY fk_attachment_notice (notice_id),
  CONSTRAINT fk_attachment_notice FOREIGN KEY (notice_id) REFERENCES notice (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 이관 대조용 (NFR-03): 이관 전후 같은 쿼리 결과가 같아야 서비스 주소를 전환한다.
-- SELECT COUNT(*) FROM notice WHERE hidden = 0;
-- SELECT COUNT(*), SUM(size_bytes) FROM attachment;
-- SELECT stored_name, sha256 FROM attachment ORDER BY id;
