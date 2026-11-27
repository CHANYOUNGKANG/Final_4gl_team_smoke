package kr.co.haedeun.notice.web;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import kr.co.haedeun.notice.domain.Category;

public class NoticeForm {
    @NotNull(message = "분류를 고르세요.")
    private Category category = Category.NOTICE;

    @NotBlank(message = "제목을 입력하세요.")
    @Size(max = 200, message = "제목은 200자까지 쓸 수 있습니다.")
    private String title;

    @NotBlank(message = "본문을 입력하세요.")
    @Size(max = 20000, message = "본문은 20,000자까지 쓸 수 있습니다.")
    private String content;

    private boolean pinned;

    public Category getCategory() { return category; }
    public void setCategory(Category category) { this.category = category; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public boolean isPinned() { return pinned; }
    public void setPinned(boolean pinned) { this.pinned = pinned; }
}
