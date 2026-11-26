# 온프레미스 공지·자료실 (JSP 임시 앱)

> **상태 (11/26)**: 온프레미스 web 서버 Tomcat 10.1 에 실제 배포해 `health.jsp` 응답과 목록 8건을 확인한 앱이다.
> 팀 표준 공지 앱은 [app/](../../app/) (Spring Boot 레퍼런스 앱, 강찬영 작성, 같은 `smoke_board` 스키마)이다.
> 이 JSP 앱은 그 앱이 병합된 것을 확인하기 전에 온프레미스 3-Tier(웹 → DB·NFS) 연결을 먼저 검증하려고 만들었다.
> **온프레미스도 app/ WAR 로 바꿀지**는 [이슈 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11) 에서 정한다.

| 항목 | 값 |
| --- | --- |
| 실행 환경 | Rocky Linux 10.3 minimal · OpenJDK 21.0.13.1 · Tomcat 10.1.61 (`/opt/tomcat`) · MariaDB Connector/J 3.3.2 (`tomcat/lib`) |
| 빌드 | `mvn -B -ntp clean package` → `target/notice.war` (11/26 배포본은 `javac` + `jar` 로 같은 구조를 만들어 배포) |
| 배포 | `/opt/tomcat/webapps/notice.war` → `/notice/` |
| DB | [server/db/smoke_board.sql](../db/smoke_board.sql) |
| 설정 | 환경 변수만 사용 — [tomcat-smoke.env.example](../configuration/web/tomcat-smoke.env.example) |

| 경로 | 내용 |
| --- | --- |
| `/notice/` | 목록 (분류: 공지·납품일정·품질인증·도면, 고정 글 우선, `is_check=1` 제외) |
| `/notice/view.jsp?id=` | 본문 · 첨부 목록 · 첨부별 SHA-256 |
| `/notice/write.jsp` | 글 + 첨부 3개(파일당 20MB). `WRITE_KEY` 필요. 업로드하면서 SHA-256 계산 → `attachment.sha256` |
| `/notice/download.jsp?fid=` | 첨부 내려받기 (저장 폴더 밖 경로 차단) |
| `/notice/latest.jsp?n=5` | 최신 글 JSON (회사 소개 페이지용) |
| `/notice/health.jsp` | DB 연결 확인 `OK notices=N` / 실패 503 |
| `/notice/check.jsp` | `POST key=$CHECK_KEY` → 검증 글 쓰기·읽기·삭제 |

검증 결과: [1126-onprem-service-check.md](../verification/1126-onprem-service-check.md)
