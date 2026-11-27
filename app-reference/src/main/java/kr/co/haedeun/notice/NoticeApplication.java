package kr.co.haedeun.notice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;

/** 외부 Tomcat(WAR)과 `java -jar`/`mvn spring-boot:run` 모두에서 실행된다. */
@SpringBootApplication
@ConfigurationPropertiesScan
public class NoticeApplication extends SpringBootServletInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(NoticeApplication.class);
    }

    public static void main(String[] args) {
        SpringApplication.run(NoticeApplication.class, args);
    }
}
