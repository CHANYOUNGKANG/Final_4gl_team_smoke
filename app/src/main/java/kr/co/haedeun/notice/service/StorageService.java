package kr.co.haedeun.notice.service;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.DigestOutputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.UUID;
import kr.co.haedeun.notice.config.AppProperties;
import org.springframework.stereotype.Service;

/**
 * 첨부파일 저장소. 온프레미스는 NFS 마운트, EKS 는 EFS 마운트 경로를 APP_STORAGE_DIR 로 준다.
 * 저장 이름은 UUID 라서 사용자가 보낸 파일명으로 경로를 만들지 않는다(경로 조작 차단).
 */
@Service
public class StorageService {

    public record Stored(String storedName, long size, String sha256) {}

    private final Path root;
    private final AppProperties props;

    public StorageService(AppProperties props) throws IOException {
        this.props = props;
        this.root = Path.of(props.storageDir()).toAbsolutePath().normalize();
        Files.createDirectories(root);
    }

    public String validateName(String originalName) {
        if (originalName == null || originalName.isBlank()) {
            throw new UploadRejectedException("파일 이름이 없습니다.");
        }
        String name = Path.of(originalName.replace('\\', '/')).getFileName().toString().strip();
        if (name.isEmpty() || name.startsWith(".") || name.length() > 200) {
            throw new UploadRejectedException("파일 이름을 확인하세요: " + name);
        }
        int dot = name.lastIndexOf('.');
        String ext = dot < 0 ? "" : name.substring(dot + 1).toLowerCase();
        if (!props.allowedExtensions().contains(ext)) {
            throw new UploadRejectedException("올릴 수 없는 형식입니다(." + ext + "). 허용: " + String.join(", ", props.allowedExtensions()));
        }
        return name;
    }

    /** 저장 이름 = UUID(32자).확장자 — smoke_board.attachment.stored_name 규칙 */
    public Stored save(InputStream in, long declaredSize, String originalName) throws IOException {
        if (declaredSize > props.maxFileBytes()) {
            throw new UploadRejectedException("파일이 너무 큽니다. 한 파일당 " + (props.maxFileBytes() / 1024 / 1024) + "MB까지 올릴 수 있습니다.");
        }
        int dot = originalName == null ? -1 : originalName.lastIndexOf('.');
        String ext = dot < 0 ? "" : originalName.substring(dot + 1).toLowerCase();
        String storedName = UUID.randomUUID().toString().replace("-", "") + (ext.isEmpty() ? "" : "." + ext);
        Path target = root.resolve(storedName);
        MessageDigest md = sha256();
        long size;
        try (OutputStream out = new DigestOutputStream(Files.newOutputStream(target), md)) {
            size = in.transferTo(out);
        }
        if (size > props.maxFileBytes()) {
            Files.deleteIfExists(target);
            throw new UploadRejectedException("파일이 너무 큽니다.");
        }
        return new Stored(storedName, size, HexFormat.of().formatHex(md.digest()));
    }

    public Path resolve(String storedName) {
        if (!storedName.matches("[0-9a-f]{32}(\\.[a-z0-9]{1,10})?")) {
            throw new IllegalArgumentException("잘못된 저장 이름");
        }
        return root.resolve(storedName);
    }

    public void delete(String storedName) {
        try {
            Files.deleteIfExists(resolve(storedName));
        } catch (IOException ignored) {
            // 파일 삭제 실패는 메타데이터 삭제를 막지 않는다. 고아 파일은 백업 점검에서 정리한다.
        }
    }

    public boolean writable() {
        return Files.isDirectory(root) && Files.isWritable(root);
    }

    private static MessageDigest sha256() {
        try {
            return MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }
}
