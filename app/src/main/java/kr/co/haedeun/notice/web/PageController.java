package kr.co.haedeun.notice.web;

import jakarta.validation.Valid;
import java.io.IOException;
import java.security.Principal;
import java.util.List;
import kr.co.haedeun.notice.domain.AdminUserRepository;
import kr.co.haedeun.notice.domain.Category;
import kr.co.haedeun.notice.domain.Notice;
import kr.co.haedeun.notice.service.NoticeService;
import kr.co.haedeun.notice.service.UploadRejectedException;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class PageController {

    private final NoticeService service;
    private final AdminUserRepository admins;

    public PageController(NoticeService service, AdminUserRepository admins) {
        this.service = service;
        this.admins = admins;
    }

    @GetMapping("/")
    public String home(Model model) {
        model.addAttribute("latest", service.latest(5));
        model.addAttribute("files", service.archive().stream().limit(4).toList());
        model.addAttribute("total", service.publicCount());
        return "home";
    }

    @GetMapping("/notices")
    public String list(@RequestParam(required = false) Category category,
                       @RequestParam(required = false) String q,
                       @RequestParam(defaultValue = "0") int page,
                       Model model) {
        Page<Notice> result = service.list(category, q, page);
        model.addAttribute("page", result);
        model.addAttribute("category", category);
        model.addAttribute("q", q == null ? "" : q);
        model.addAttribute("categories", Category.values());
        return "notices/list";
    }

    @GetMapping("/notices/{id}")
    public String detail(@PathVariable int id, Model model) {
        model.addAttribute("notice", service.read(id));
        return "notices/detail";
    }

    @GetMapping("/archive")
    public String archive(Model model) {
        model.addAttribute("files", service.archive());
        return "archive";
    }

    @GetMapping("/notices/new")
    public String form(Model model) {
        model.addAttribute("form", new NoticeForm());
        model.addAttribute("categories", Category.values());
        return "notices/form";
    }

    @PostMapping("/notices/new")
    public String create(@Valid @ModelAttribute("form") NoticeForm form, BindingResult binding,
                         @RequestParam(name = "files", required = false) List<MultipartFile> files,
                         Principal principal, Model model, RedirectAttributes ra) throws IOException {
        if (!binding.hasErrors()) {
            try {
                // writer = 관리자 표시 이름(admin_user.display_name)
                String writer = admins.findByUsername(principal.getName()).map(a -> a.getDisplayName()).orElse(principal.getName());
                Notice saved = service.create(form.getCategory(), form.getTitle(), form.getContent(),
                        writer, form.isPinned(), false, files);
                ra.addFlashAttribute("flash", "공지를 게시했습니다. 문서번호 " + saved.getDocNo());
                return "redirect:/notices/" + saved.getId();
            } catch (UploadRejectedException e) {
                model.addAttribute("uploadError", e.getMessage());
            }
        }
        model.addAttribute("categories", Category.values());
        return "notices/form";
    }

    @PostMapping("/notices/{id}/delete")
    public String delete(@PathVariable int id, RedirectAttributes ra) {
        service.delete(id);
        ra.addFlashAttribute("flash", "공지를 삭제했습니다.");
        return "redirect:/notices";
    }

    @GetMapping("/login")
    public String login() {
        return "login";
    }
}
