package kr.co.haedeun.notice.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import kr.co.haedeun.notice.domain.AdminUserRepository;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.header.writers.ReferrerPolicyHeaderWriter;

@Configuration
public class SecurityConfig {

    /** admin_user.password_hash 는 bcrypt($2a$/$2b$/$2y$) 해시만 저장한다 (smoke_board.sql 규칙). */
    @Bean
    PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /** 관리자 로그인 = smoke_board.admin_user 조회. */
    @Bean
    UserDetailsService users(AdminUserRepository admins) {
        return username -> admins.findByUsername(username)
                .map(a -> User.withUsername(a.getUsername()).password(a.getPasswordHash()).roles("ADMIN").build())
                .orElseThrow(() -> new UsernameNotFoundException("관리자 계정이 없습니다"));
    }

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(a -> a
                .requestMatchers("/notices/new", "/notices/*/delete").hasRole("ADMIN")
                // /api/** 는 X-Check-Token 으로 CheckApiController 에서 직접 검사한다
                .anyRequest().permitAll())
            .formLogin(f -> f.loginPage("/login").defaultSuccessUrl("/notices", false).permitAll())
            .logout(l -> l.logoutUrl("/logout").logoutSuccessUrl("/"))
            .csrf(c -> c.ignoringRequestMatchers("/api/**"))
            .headers(h -> h
                .contentSecurityPolicy(csp -> csp.policyDirectives(
                    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                    + "frame-ancestors 'none'; form-action 'self'; base-uri 'self'"))
                .referrerPolicy(r -> r.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.SAME_ORIGIN)));
        return http.build();
    }
}
