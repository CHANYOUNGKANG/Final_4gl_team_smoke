package kr.co.haedeun.notice.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 첨부파일 메타데이터. 실제 파일은 storedName(UUID)으로 저장소(로컬 디렉터리·NFS·EFS)에 둔다.
 * sha256 은 이관 전후 대조(NFR-03)에 그대로 쓴다.
 */
@Entity
@Table(name = "attachment")
public class Attachment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "notice_id")
    private Notice notice;

    @Column(name = "original_name", nullable = false, length = 255)
    private String originalName;

    @Column(name = "stored_name", nullable = false, length = 64, unique = true)
    private String storedName;

    @Column(name = "content_type", length = 100)
    private String contentType;

    @Column(name = "size_bytes", nullable = false)
    private long size;

    @Column(nullable = false, length = 64)
    private String sha256;

    @Column(name = "download_count", nullable = false)
    private long downloadCount;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    protected Attachment() {}

    public Attachment(String originalName, String storedName, String contentType, long size, String sha256) {
        this.originalName = originalName;
        this.storedName = storedName;
        this.contentType = contentType;
        this.size = size;
        this.sha256 = sha256;
        this.createdAt = LocalDateTime.now();
    }

    void setNotice(Notice notice) { this.notice = notice; }
    public void increaseDownload() { downloadCount++; }

    public String getExtension() {
        int i = originalName.lastIndexOf('.');
        return i < 0 ? "" : originalName.substring(i + 1).toLowerCase();
    }

    public String getHumanSize() {
        if (size < 1024) return size + " B";
        if (size < 1024 * 1024) return "%.1f KB".formatted(size / 1024.0);
        return "%.1f MB".formatted(size / 1024.0 / 1024.0);
    }

    public Long getId() { return id; }
    public Notice getNotice() { return notice; }
    public String getOriginalName() { return originalName; }
    public String getStoredName() { return storedName; }
    public String getContentType() { return contentType; }
    public long getSize() { return size; }
    public String getSha256() { return sha256; }
    public long getDownloadCount() { return downloadCount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
