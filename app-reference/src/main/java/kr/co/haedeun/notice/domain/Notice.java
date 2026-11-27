package kr.co.haedeun.notice.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/** server/db/smoke_board.sql 의 notice 테이블 (이준호 작성 스키마 기준). */
@Entity
@Table(name = "notice")
public class Notice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "notice_id", columnDefinition = "INT")
    private Integer id;

    @Column(name = "category", nullable = false, length = 20)
    private Category category;

    @Column(name = "title", nullable = false, length = 200)
    private String title;

    // @Lob(CLOB)으로 두면 검색 쿼리의 lower()가 실패한다 → TEXT 문자열 컬럼으로 매핑
    @Column(name = "content", nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(name = "writer", nullable = false, length = 50)
    private String writer;

    @Column(name = "is_pinned", nullable = false, columnDefinition = "TINYINT(1)")
    private boolean pinned;

    /** 배포 검증(공지 작성·조회 검사)용 글. 공개 목록과 이관 건수에서 뺀다. */
    @Column(name = "is_check", nullable = false, columnDefinition = "TINYINT(1)")
    private boolean checkPost;

    @Column(name = "view_count", nullable = false, columnDefinition = "INT")
    private int viewCount;

    @Column(name = "created_at", nullable = false, columnDefinition = "DATETIME")
    private LocalDateTime createdAt;

    @Column(name = "updated_at", columnDefinition = "DATETIME")
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "notice", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("id ASC")
    private List<Attachment> attachments = new ArrayList<>();

    protected Notice() {}

    public Notice(Category category, String title, String content, String writer, boolean pinned, boolean checkPost) {
        this.category = category;
        this.title = title;
        this.content = content;
        this.writer = writer;
        this.pinned = pinned;
        this.checkPost = checkPost;
        this.createdAt = LocalDateTime.now().withNano(0);
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

    public Integer getId() { return id; }
    public Category getCategory() { return category; }
    public String getTitle() { return title; }
    public String getContent() { return content; }
    public String getWriter() { return writer; }
    public boolean isPinned() { return pinned; }
    public boolean isCheckPost() { return checkPost; }
    public int getViewCount() { return viewCount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public List<Attachment> getAttachments() { return attachments; }
}
