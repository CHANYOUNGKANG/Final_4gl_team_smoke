package kr.co.haedeun.notice.domain;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/** server/db/smoke_board.sql 의 admin_user 테이블. 비밀번호는 bcrypt 해시만 저장한다. */
@Entity
@Table(name = "admin_user")
public class AdminUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id", columnDefinition = "INT")
    private Integer id;

    @Column(name = "username", nullable = false, length = 50, unique = true)
    private String username;

    @Column(name = "password_hash", nullable = false, length = 100)
    private String passwordHash;

    @Column(name = "display_name", nullable = false, length = 50)
    private String displayName;

    @Column(name = "created_at", nullable = false, columnDefinition = "DATETIME")
    private LocalDateTime createdAt;

    protected AdminUser() {}

    public AdminUser(String username, String passwordHash, String displayName) {
        this.username = username;
        this.passwordHash = passwordHash;
        this.displayName = displayName;
        this.createdAt = LocalDateTime.now().withNano(0);
    }

    public Integer getId() { return id; }
    public String getUsername() { return username; }
    public String getPasswordHash() { return passwordHash; }
    public String getDisplayName() { return displayName; }
}
