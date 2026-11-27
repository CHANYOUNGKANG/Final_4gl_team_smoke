package kr.co.haedeun.notice.web;

import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@ControllerAdvice
public class UploadErrorAdvice {

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public String tooLarge(RedirectAttributes ra) {
        ra.addFlashAttribute("flash", "첨부파일이 너무 큽니다. 한 번에 올리는 파일 합계를 줄여 다시 올리세요.");
        return "redirect:/notices/new";
    }
}
