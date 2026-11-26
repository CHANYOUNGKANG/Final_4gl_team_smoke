package kr.co.haedeun.notice.web;

import java.nio.charset.StandardCharsets;
import kr.co.haedeun.notice.domain.Attachment;
import kr.co.haedeun.notice.service.NoticeService;
import kr.co.haedeun.notice.service.StorageService;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class FileController {

    private final NoticeService service;
    private final StorageService storage;

    public FileController(NoticeService service, StorageService storage) {
        this.service = service;
        this.storage = storage;
    }

    @GetMapping("/files/{id}")
    public ResponseEntity<Resource> download(@PathVariable long id) {
        Attachment a = service.download(id);
        FileSystemResource file = new FileSystemResource(storage.resolve(a.getStoredName()));
        if (!file.exists()) {
            return ResponseEntity.status(410).build();
        }
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, ContentDisposition.attachment()
                        .filename(a.getOriginalName(), StandardCharsets.UTF_8).build().toString())
                .header("X-Content-SHA256", a.getSha256())
                .header("X-Content-Type-Options", "nosniff")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .contentLength(a.getSize())
                .body(file);
    }
}
