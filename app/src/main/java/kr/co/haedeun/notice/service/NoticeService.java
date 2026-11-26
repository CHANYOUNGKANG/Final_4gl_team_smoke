package kr.co.haedeun.notice.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import kr.co.haedeun.notice.domain.*;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class NoticeService {

    public static final int PAGE_SIZE = 10;

    private final NoticeRepository notices;
    private final AttachmentRepository attachments;
    private final StorageService storage;

    public NoticeService(NoticeRepository notices, AttachmentRepository attachments, StorageService storage) {
        this.notices = notices;
        this.attachments = attachments;
        this.storage = storage;
    }

    @Transactional(readOnly = true)
    public Page<Notice> list(Category category, String q, int page) {
        String query = (q == null || q.isBlank()) ? null : q.strip();
        return notices.search(category, query, PageRequest.of(Math.max(page, 0), PAGE_SIZE));
    }

    @Transactional(readOnly = true)
    public List<Notice> latest(int size) {
        return notices.search(null, null, PageRequest.of(0, size)).getContent();
    }

    @Transactional(readOnly = true)
    public List<Attachment> archive() {
        return attachments.findAllPublic();
    }

    /** 공개 화면용 조회. 검증용 숨김 글은 404. */
    @Transactional
    public Notice read(long id) {
        Notice n = notices.findById(id).filter(x -> !x.isHidden())
                .orElseThrow(() -> new NotFoundException("공지 " + id + "번이 없습니다."));
        n.increaseView();
        n.getAttachments().size();
        return n;
    }

    /** 검증 API용 조회. 숨김 글 포함, 조회수는 올리지 않는다. */
    @Transactional(readOnly = true)
    public Notice readForCheck(long id) {
        Notice n = notices.findById(id).orElseThrow(() -> new NotFoundException("공지 " + id + "번이 없습니다."));
        n.getAttachments().size();
        return n;
    }

    @Transactional
    public Notice create(Category category, String title, String content, String author,
                         boolean pinned, boolean hidden, List<MultipartFile> files) throws IOException {
        Notice n = new Notice(category, title.strip(), content.strip(), author, pinned, hidden);
        if (files != null) {
            for (MultipartFile f : files) {
                if (f == null || f.isEmpty()) continue;
                String name = storage.validateName(f.getOriginalFilename());
                try (InputStream in = f.getInputStream()) {
                    StorageService.Stored s = storage.save(in, f.getSize());
                    n.addAttachment(new Attachment(name, s.storedName(), f.getContentType(), s.size(), s.sha256()));
                }
            }
        }
        return notices.save(n);
    }

    @Transactional
    public void delete(long id) {
        Notice n = notices.findById(id).orElseThrow(() -> new NotFoundException("공지 " + id + "번이 없습니다."));
        n.getAttachments().forEach(a -> storage.delete(a.getStoredName()));
        notices.delete(n);
    }

    @Transactional
    public Attachment download(long attachmentId) {
        Attachment a = attachments.findById(attachmentId)
                .filter(x -> !x.getNotice().isHidden())
                .orElseThrow(() -> new NotFoundException("첨부파일 " + attachmentId + "번이 없습니다."));
        a.increaseDownload();
        return a;
    }

    @Transactional(readOnly = true)
    public long publicCount() {
        return notices.countByHiddenFalse();
    }
}
