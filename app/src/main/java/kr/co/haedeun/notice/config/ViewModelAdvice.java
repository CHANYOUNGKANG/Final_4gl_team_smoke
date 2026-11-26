package kr.co.haedeun.notice.config;

import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ModelAttribute;

/** 모든 화면 하단에 배포 버전·슬롯을 표시한다 → 블루그린 전환을 브라우저에서 바로 확인. */
@ControllerAdvice(annotations = org.springframework.stereotype.Controller.class)
public class ViewModelAdvice {

    private final AppProperties props;

    public ViewModelAdvice(AppProperties props) {
        this.props = props;
    }

    @ModelAttribute("build")
    public AppProperties build() {
        return props;
    }
}
