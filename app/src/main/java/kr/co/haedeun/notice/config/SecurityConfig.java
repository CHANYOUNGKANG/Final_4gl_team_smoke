package kr.co.haedeun.notice.config;

import java.util.ArrayList;
import java.util.List;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.header.writers.ReferrerPolicyHeaderWriter;

@Configuration
public class SecurityConfig {

    @Bean
    PasswordEncoder passwordEncoder() {
        return PasswordEncoderFactories.createDelegatingPasswordEncoder();
    }

    /** ADMIN_PASSWORD 가 없으면 관리자 계정을 만들지 않는다 → 글쓰기 화면은 로그인 불가 상태로 남는다. */
    @Bean
    UserDetailsService users(AppProperties props, PasswordEncoder encoder) {
        List<UserDetails> list = new ArrayList<>();
        if (props.adminEnabled()) {
            list.add(User.withUsername(props.adminUsername())
                    .password(encoder.encode(props.adminPassword()))
                    .roles("ADMIN")
                    .build());
        }
        return new InMemoryUserDetailsManager(list);
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
