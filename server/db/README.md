# 공지·자료실 DB (`smoke_board`)

작성: 이준호 · 대상: 데이터 서버 MariaDB 10.11 · 문자셋 `utf8mb4` / `utf8mb4_unicode_ci`

| 파일 | 내용 |
| --- | --- |
| [smoke_board.sql](smoke_board.sql) | DB·테이블(`admin_user`, `notice`, `attachment`)·샘플 글 8건·이관 대조 뷰 `v_migration_check`·앱 계정 |

```bash
sudo mysql -u root -p < smoke_board.sql      # 처음 구축용: 기존 테이블을 지우고 다시 만든다
```

- 앱 계정 비밀번호는 파일의 `'비밀번호'` 자리를 **실행할 때만** 실제 값으로 바꾼다. 바꾼 파일은 커밋하지 않는다.
- `'smoke'@'192.168.111.%'` 는 NAT 작업용 임시 계정 → 연동 후 `DROP USER`.
- 이관 전후 대조: `SELECT * FROM v_migration_check;` 결과(건수·본문 해시·파일 해시)가 온프레미스와 RDS에서 같아야 주소를 전환한다.
