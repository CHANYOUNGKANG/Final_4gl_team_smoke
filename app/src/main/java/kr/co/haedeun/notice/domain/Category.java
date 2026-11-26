package kr.co.haedeun.notice.domain;

/** 공지 분류. 문서번호 접두어(code)는 게시판 목록의 "도면 표제란" 표기에 쓴다. */
public enum Category {
    NOTICE("공지", "GN"),
    DELIVERY("납품·물류", "DL"),
    QUALITY("품질·인증", "QA"),
    ARCHIVE("자료실", "DC");

    private final String label;
    private final String code;

    Category(String label, String code) {
        this.label = label;
        this.code = code;
    }

    public String getLabel() { return label; }
    public String getCode() { return code; }
}
