package kr.co.haedeun.notice;

import static org.hamcrest.Matchers.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestBuilders.formLogin;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.response.SecurityMockMvcResultMatchers.authenticated;
import static org.springframework.security.test.web.servlet.response.SecurityMockMvcResultMatchers.unauthenticated;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import kr.co.haedeun.notice.domain.AdminUserRepository;
import kr.co.haedeun.notice.domain.AttachmentRepository;
import kr.co.haedeun.notice.domain.NoticeRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class NoticeAppTests {

    static final String TOKEN = "test-check-token-0123456789";

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper json;
    @Autowired AttachmentRepository attachments;
    @Autowired AdminUserRepository admins;
    @Autowired NoticeRepository notices;

    @Test
    void 상태검사는_버전과_DB_저장소_상태를_돌려준다() throws Exception {
        mvc.perform(get("/health"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.status").value("UP"))
           .andExpect(jsonPath("$.db").value("UP"))
           .andExpect(jsonPath("$.storage").value("UP"))
           .andExpect(jsonPath("$.version").isNotEmpty())
           .andExpect(jsonPath("$.color").value("local"));
    }

    @Test
    void 공지_목록과_홈은_로그인없이_열린다() throws Exception {
        mvc.perform(get("/")).andExpect(status().isOk()).andExpect(content().string(containsString("최근 공지")));
        mvc.perform(get("/notices")).andExpect(status().isOk())
           .andExpect(content().string(containsString("ISO 9001")));
        mvc.perform(get("/archive")).andExpect(status().isOk());
    }

    @Test
    void 보안헤더가_붙는다() throws Exception {
        mvc.perform(get("/notices"))
           .andExpect(header().string("Content-Security-Policy", containsString("default-src 'self'")))
           .andExpect(header().string("X-Frame-Options", "DENY"));
    }

    @Test
    void 공지쓰기는_관리자만_할수있다() throws Exception {
        mvc.perform(get("/notices/new")).andExpect(status().is3xxRedirection())
           .andExpect(redirectedUrlPattern("**/login"));
        mvc.perform(get("/notices/new").with(user("admin").roles("ADMIN"))).andExpect(status().isOk());
    }

    @Test
    void 관리자가_첨부와_함께_공지를_올리면_해시가_기록되고_같은_파일이_내려온다() throws Exception {
        byte[] body = "도면 Rev.D 샘플".getBytes(StandardCharsets.UTF_8);
        String expected = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(body));

        String location = mvc.perform(multipart("/notices/new")
                .file(new MockMultipartFile("files", "HS-2440_도면.txt", "text/plain", body))
                .param("category", "DRAWING").param("title", "HS-2440 도면 개정").param("content", "Rev.D 반영")
                .with(user("admin").roles("ADMIN")).with(csrf()))
            .andExpect(status().is3xxRedirection())
            .andReturn().getResponse().getRedirectedUrl();

        mvc.perform(get(location)).andExpect(status().isOk()).andExpect(content().string(containsString(expected)));

        int fileId = attachments.findAll().stream().filter(a -> a.getSha256().equals(expected)).findFirst().orElseThrow().getId();
        mvc.perform(get("/files/" + fileId))
           .andExpect(status().isOk())
           .andExpect(header().string("X-Content-SHA256", expected))
           .andExpect(header().string("Content-Disposition", containsString("attachment")))
           .andExpect(content().bytes(body));
    }

    @Test
    void 허용하지_않은_확장자와_경로조작_파일명은_거부한다() throws Exception {
        mvc.perform(multipart("/notices/new")
                .file(new MockMultipartFile("files", "shell.jsp", "text/plain", "x".getBytes()))
                .param("category", "NOTICE").param("title", "t").param("content", "c")
                .with(user("admin").roles("ADMIN")).with(csrf()))
           .andExpect(status().isOk())
           .andExpect(content().string(containsString("올릴 수 없는 형식")));

        mvc.perform(multipart("/notices/new")
                .file(new MockMultipartFile("files", "../../.bashrc", "text/plain", "x".getBytes()))
                .param("category", "NOTICE").param("title", "t").param("content", "c")
                .with(user("admin").roles("ADMIN")).with(csrf()))
           .andExpect(status().isOk())
           .andExpect(content().string(containsString("파일 이름을 확인하세요")));
    }

    @Test
    void 검증API는_토큰이_없으면_401이고_검증글은_공개목록에_보이지_않는다() throws Exception {
        String req = "{\"title\":\"배포 검증 글 build-42\",\"content\":\"green check\"}";
        mvc.perform(post("/api/check/notices").contentType(MediaType.APPLICATION_JSON).content(req))
           .andExpect(status().isUnauthorized());

        String res = mvc.perform(post("/api/check/notices").header("X-Check-Token", TOKEN)
                .contentType(MediaType.APPLICATION_JSON).content(req))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.servedBy.version").isNotEmpty())
            .andReturn().getResponse().getContentAsString(StandardCharsets.UTF_8);
        JsonNode node = json.readTree(res);
        int id = node.get("id").asInt();

        mvc.perform(get("/api/check/notices/" + id).header("X-Check-Token", TOKEN))
           .andExpect(status().isOk()).andExpect(jsonPath("$.title").value("배포 검증 글 build-42"));
        mvc.perform(get("/notices")).andExpect(content().string(not(containsString("배포 검증 글 build-42"))));
        mvc.perform(get("/notices/" + id)).andExpect(status().isNotFound());

        mvc.perform(delete("/api/check/notices/" + id).header("X-Check-Token", TOKEN)).andExpect(status().isNoContent());
        mvc.perform(get("/api/check/notices/" + id).header("X-Check-Token", TOKEN)).andExpect(status().isNotFound());
    }

    @Test
    void 검증API로_고객공지는_지울수없다() throws Exception {
        mvc.perform(delete("/api/check/notices/1").header("X-Check-Token", TOKEN)).andExpect(status().isConflict());
    }

    @Test
    void 관리자는_admin_user_테이블의_bcrypt_해시로_로그인한다() throws Exception {
        String hash = admins.findByUsername("admin").orElseThrow().getPasswordHash();
        org.junit.jupiter.api.Assertions.assertTrue(hash.startsWith("$2"), "bcrypt 해시만 저장해야 한다");
        mvc.perform(formLogin("/login").user("admin").password("test-admin-pass")).andExpect(authenticated());
        mvc.perform(formLogin("/login").user("admin").password("wrong-pass")).andExpect(unauthenticated());
    }

    @Test
    void 분류는_DB에_한글값으로_저장되고_샘플은_smoke_board와_같은_8건이다() throws Exception {
        org.junit.jupiter.api.Assertions.assertTrue(notices.countByCheckPostFalse() >= 8);
        mvc.perform(get("/notices").param("category", "DRAWING"))
           .andExpect(status().isOk())
           .andExpect(content().string(containsString("B-207 플랜지 도면 Rev.C")))
           .andExpect(content().string(not(containsString("ISO 9001 인증서"))));
    }
}
