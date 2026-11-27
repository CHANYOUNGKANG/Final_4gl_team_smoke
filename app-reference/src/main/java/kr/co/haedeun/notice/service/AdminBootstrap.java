package kr.co.haedeun.notice.service;

import kr.co.haedeun.notice.config.AppProperties;
import kr.co.haedeun.notice.domain.AdminUser;
import kr.co.haedeun.notice.domain.AdminUserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 첫 관리자 계정 만들기. ADMIN_PASSWORD 가 주어지고 admin_user 에 ADMIN_USERNAME 이 없을 때만
 * bcrypt 해시로 한 줄을 넣는다(이미 있으면 아무것도 바꾸지 않는다). 비밀번호 원문은 저장·출력하지 않는다.
 */
@Component
@Order(1)
public class AdminBootstrap implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(AdminBootstrap.class);

    private final AppProperties props;
    private final AdminUserRepository admins;
    private final PasswordEncoder encoder;

    public AdminBootstrap(AppProperties props, AdminUserRepository admins, PasswordEncoder encoder) {
        this.props = props;
        this.admins = admins;
        this.encoder = encoder;
    }

    @Override
    @Transactional
    public void run(ApplicationArguments args) {
        if (!props.adminEnabled() || admins.findByUsername(props.adminUsername()).isPresent()) return;
        admins.save(new AdminUser(props.adminUsername(), encoder.encode(props.adminPassword()), props.adminDisplayName()));
        log.info("관리자 계정 '{}'을 admin_user 에 만들었습니다.", props.adminUsername());
    }
}
