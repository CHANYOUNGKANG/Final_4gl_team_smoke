# 공지 웹앱 · ㈜스모크 회사 사이트 + 공지·자료실

[서버 담당](../server/README.md) · [CI/CD 담당](../cicd/README.md) · [Docker 이미지](../cicd/docker/README.md) · [이전 레퍼런스 앱](../app-reference/README.md)

온프레미스(web 서버 Tomcat 10.1)에서 실제로 운영·검증한 앱을 팀 표준으로 삼는다 (11/27 팀 합의, 이준호 · 강찬영).
회사 홈페이지(회사소개·사업분야·인프라·문의)와 공지·자료실, 첨부 SHA-256 저장, 문의 → 사내 메일 알림을 한 WAR 로 제공한다.
CI/CD 가 쓰던 상태 검사·버전·검증 API 규격은 이전 레퍼런스 앱과 **같은 주소, 같은 응답 형식**으로 유지한다.

| 항목 | 값 |
| --- | --- |
| 기술 | JSP + 서블릿 1개, Java 17 (온프레미스 Java 21에서도 동작), Tomcat 10.1 (Jakarta EE 10) |
| 빌드 | `app/` 에서 `mvn -B -ntp clean package` → `target/notice.war` (Tomcat·Docker 에서는 `ROOT.war` 로 배치) |
| 단위 테스트 | `src/test/java/kr/smoke/site/SiteUtilTest.java` (JSON · 토큰 비교 · 커밋 표시 · SHA-256 · 메일 헤더 주입 방지) |
| DB | MariaDB 10.11 / RDS `boarddb` — 스키마 [sql/schema.sql](sql/schema.sql), 예시 글 [sql/sample_data.sql](sql/sample_data.sql) |
| DB 설정이 없을 때 | H2 메모리 DB 로 뜬다 (CI·로컬 격리 검증용, 예시 글 4건 자동 입력) |

## CI/CD 규격 (강찬영 요청 · 11/27)

| 주소 | 응답 |
| --- | --- |
| `GET /health` | 200 `{"status":"UP","db":"UP","storage":"UP","app":"haedeun-notice","version":…,"color":…,"commit":…}` · `db=UP` 은 접속 + 필수 테이블·컬럼(board·board_file·inquiry) 정상일 때만, 하나라도 안 되면 503 |
| `GET /version` | `{"app":"haedeun-notice","version":…,"color":…,"commit":…}` (commit = `GIT_COMMIT` 앞 7자리) |
| `GET /notices` | 200 공지 목록 |
| `GET /notices/{id}` | 공지 상세 (= `/view.jsp?id={id}`), 검증 글·없는 글은 404 |
| `POST /api/check/notices` | 헤더 `X-Check-Token`, 본문 `{"title","content"}` → 201 + `Location` + `{"id","docNo","title","content","servedBy":{"version","color","commit"}}` |
| `GET /api/check/notices/{id}` | 200 / 없으면 404 |
| `DELETE /api/check/notices/{id}` | 204 (검증 글이 아니면 409) → 다시 조회하면 404 |
| 토큰 | `CHECK_TOKEN` 이 없으면 검증 API 전체 404, 헤더가 다르면 401 |

검증 글은 `board.is_check = 1` 로 저장되고 공개 목록·메인 최신 글·상세(404)·`v_migration_check` 건수에서 빠진다.
PR 검사 [.github/workflows/app-build.yml](../.github/workflows/app-build.yml) 이 Tomcat 10.1 컨테이너에 WAR 를 올려 위 순서를 그대로 확인한다.

## 환경 변수

| 변수 | 구분 | 설명 |
| --- | --- | --- |
| `DB_HOST` `DB_PORT`(3306) `DB_NAME`(boarddb) `DB_USER` | 설정 | MariaDB/RDS 접속. `DB_URL` 을 직접 줘도 된다 (`DB_URL` 이 우선) |
| `DB_PASSWORD` | **비밀** | 온프레미스 예전 이름 `DB_PASS` 도 읽는다 |
| `APP_STORAGE_DIR` | 설정 | 첨부 저장 경로. 온프레미스 `/var/smoke/attach`(NFS), 컨테이너 기본 `/data/attachments`. 예전 이름 `UPLOAD_DIR` 도 읽는다 |
| `FILE_BASE_URL` | 설정 | S3·CloudFront 로 이관 후 내려받기를 그 주소로 넘긴다 (비우면 앱이 직접 전송) |
| `DEPLOY_COLOR` `APP_VERSION` `GIT_COMMIT` | 설정 | 화면 하단 · `/health` · `/version` · `servedBy` |
| `CHECK_TOKEN` | **비밀** | 검증 API 토큰 (Jenkins Credentials 같은 값) |
| `ADMIN_KEY` | **비밀** | 공지 쓰기 관리자 키. 운영(MariaDB)에서 비어 있으면 공지 쓰기 자체가 꺼진다 (H2 만 키 없이 허용) |
| `DB_DDL` | 설정 | `validate`(운영 기본): 앱은 테이블을 만들지 않고 확인만, 앱 계정은 SELECT·INSERT·UPDATE·DELETE 만 · `update`(H2 기본): 앱이 테이블 생성 |
| `APP_SEED` | 설정 | 예시 글 입력. H2 기본 `true`, MariaDB 기본 `false` (이관 데이터 건수 보존) |
| `MAIL_TO` `MAIL_FROM` `SMTP_HOST` `SMTP_PORT` | 설정 | 문의 접수 메일 알림. `MAIL_TO` 를 비우면 알림 끔 (AWS 기본) |
| `COMPANY_ADDR` `COMPANY_TEL` `COMPANY_MAIL` | 설정 | 화면에 보이는 회사 연락처 |

저장소에는 실제 주소·비밀번호를 두지 않는다. 온프레미스는 `/etc/tomcat-smoke.env`, EKS 는 ConfigMap·Secret 으로 넣는다.

## 데이터 무결성 (이관 검증)

- 첨부 업로드 시 SHA-256 을 계산해 `board_file.sha256` 에 저장, 상세 화면에 표시
- 저장 이름 `YYYYMM/UUID.확장자` = S3 키 그대로
- `v_migration_check` : 게시글·첨부·문의 건수 + 본문·첨부 목록 해시. 온프레미스와 RDS 에서 같은 값이면 이관 성공
- 백업·복구 검증과 인계 자료 수집은 [server/](../server/README.md) 참고

## 온프레미스 배포

```bash
sudo systemctl stop tomcat
sudo cp notice.war /opt/tomcat/webapps/ROOT.war && sudo chown tomcat:tomcat /opt/tomcat/webapps/ROOT.war
sudo systemctl start tomcat && sleep 10
curl -s http://127.0.0.1/health; echo
```
