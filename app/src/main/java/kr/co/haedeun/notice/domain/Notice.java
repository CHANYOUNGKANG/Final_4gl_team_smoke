package kr.co.haedeun.notice.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "notice", indexes = {
        @Index(name = "idx_notice_list", columnList = "hidden, pinned, created_at")
})
public class Notice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private Category category;

    @Column(nullable = false, length = 200)
    private String title;

    @Lob
    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(nullable = false, length = 50)
    private String author;

    @Column(nullable = false)
    private boolean pinned;

    /** 배포 검증(공지 작성·조회 검사)용 글. 공개 목록에는 보이지 않는다. */
    @Column(nullable = false)
    private boolean hidden;

    @Column(name = "view_count", nullable = false)
    private long viewCount;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "notice", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("id ASC")
    private List<Attachment> attachments = new ArrayList<>();

    protected Notice() {}

    public Notice(Category category, String title, String content, String author, boolean pinned, boolean hidden) {
        this.category = category;
        this.title = title;
        this.content = content;
        this.author = author;
        this.pinned = pinned;
        this.hidden = hidden;
        this.createdAt = LocalDateTime.now();
    }

    /** 표제란 문서번호 예: QA-2026-0012 */
    public String getDocNo() {
        return "%s-%d-%04d".formatted(category.getCode(), createdAt.getYear(), id == null ? 0 : id);
    }

    public boolean isNew() {
        return createdAt.isAfter(LocalDateTime.now().minusDays(7));
    }

    public void addAttachment(Attachment a) {
        attachments.add(a);
        a.setNotice(this);
    }

    public void increaseView() { viewCount++; }
    public void backdate(LocalDateTime at) { this.createdAt = at; }

    public Long getId() { return id; }
    public Category getCategory() { return category; }
    public String getTitle() { return title; }
    public String getContent() { return content; }
    public String getAuthor() { return author; }
    public boolean isPinned() { return pinned; }
    public boolean isHidden() { return hidden; }
    public long getViewCount() { return viewCount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public List<Attachment> getAttachments() { return attachments; }
}
