package kr.co.haedeun.notice.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * server/db/smoke_board.sql 의 attachment 테이블.
 * 실제 파일은 stored_name(UUID.확장자)으로 저장소(APP_STORAGE_DIR = NFS /share/attach → 이관 후 S3)에 둔다.
 * sha256 은 업로드 때 계산해 저장 → 이관 전후 대조 기준(v_migration_check).
 */
@Entity
@Table(name = "attachment")
public class Attachment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "file_id", columnDefinition = "INT")
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "notice_id", nullable = false, columnDefinition = "INT")
    private Notice notice;

    @Column(name = "orig_name", nullable = false, length = 255)
    private String originalName;

    @Column(name = "stored_name", nullable = false, length = 100, unique = true)
    private String storedName;

    @Column(name = "file_size", nullable = false)
    private long size;

    @Column(name = "mime_type", length = 100)
    private String contentType;

    @Column(name = "sha256", nullable = false, columnDefinition = "CHAR(64)")
    private String sha256;

    @Column(name = "uploaded_at", nullable = false, columnDefinition = "DATETIME")
    private LocalDateTime uploadedAt;

    protected Attachment() {}

    public Attachment(String originalName, String storedName, String contentType, long size, String sha256) {
        this.originalName = originalName;
        this.storedName = storedName;
        this.contentType = contentType;
        this.size = size;
        this.sha256 = sha256;
        this.uploadedAt = LocalDateTime.now().withNano(0);
    }

    void setNotice(Notice notice) { this.notice = notice; }

    public String getExtension() {
        int i = originalName.lastIndexOf('.');
        return i < 0 ? "" : originalName.substring(i + 1).toLowerCase();
    }

    public String getHumanSize() {
        if (size < 1024) return size + " B";
        if (size < 1024 * 1024) return "%.1f KB".formatted(size / 1024.0);
        return "%.1f MB".formatted(size / 1024.0 / 1024.0);
    }

    public Integer getId() { return id; }
    public Notice getNotice() { return notice; }
    public String getOriginalName() { return originalName; }
    public String getStoredName() { return storedName; }
    public String getContentType() { return contentType; }
    public long getSize() { return size; }
    public String getSha256() { return sha256; }
    public LocalDateTime getUploadedAt() { return uploadedAt; }
}
