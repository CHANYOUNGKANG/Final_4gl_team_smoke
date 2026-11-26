package kr.co.haedeun.notice.domain;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

/**
 * 공지 분류. DB(server/db/smoke_board.sql)의 CHECK 제약과 같은 한글 값('공지','납품일정','품질인증','도면')으로 저장한다.
 * code 는 화면의 문서번호 접두어.
 */
public enum Category {
    NOTICE("공지", "GN"),
    DELIVERY("납품일정", "DL"),
    QUALITY("품질인증", "QA"),
    DRAWING("도면", "DW");

    private final String label;
    private final String code;

    Category(String label, String code) {
        this.label = label;
        this.code = code;
    }

    public String getLabel() { return label; }
    public String getCode() { return code; }

    public static Category fromLabel(String label) {
        for (Category c : values()) {
            if (c.label.equals(label)) return c;
        }
        throw new IllegalArgumentException("알 수 없는 분류: " + label);
    }

    @Converter(autoApply = true)
    public static class DbConverter implements AttributeConverter<Category, String> {
        @Override public String convertToDatabaseColumn(Category c) { return c == null ? null : c.label; }
        @Override public Category convertToEntityAttribute(String v) { return v == null ? null : fromLabel(v); }
    }
}
