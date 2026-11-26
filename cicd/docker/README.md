# Docker 이미지 (CICD2)

[CI/CD 홈](../README.md) · [앱 인계표](../../app/README.md)

| 항목 | 값 |
| --- | --- |
| 베이스 | `tomcat:10.1-jre17-temurin` (Spring Boot 3 = Jakarta EE 10 → Tomcat 10.1 필요) |
| 배치 | `app/target/notice.war` → `webapps/ROOT.war` (컨텍스트 `/`) |
| 포트 | `8080` = ALB 대상 그룹 포트 (`APP_PORT`) |
| 상태 검사 | `GET /health` → 200 `{"status":"UP","db":"UP","storage":"UP","version":…,"color":…}` |
| 태그 | 커밋 SHA 7자리 (`notice:abc1234`) · `latest` 태그는 쓰지 않는다 |
| 사용자 | 비루트 `app` |
| 첨부 저장소 | `/data/attachments` ← NFS(온프레미스) / EFS PVC(EKS) |

런타임에 주입하는 값 (Kubernetes ConfigMap·Secret):

| 변수 | 구분 | 설명 |
| --- | --- | --- |
| `DEPLOY_COLOR` | ConfigMap | `blue` / `green` — 화면 상단 막대와 하단 배지 색, `/version` 응답 |
| `APP_VERSION` | ConfigMap | 비우면 `pom.xml` 버전 |
| `DB_HOST` `DB_PORT` `DB_NAME`(기본 `smoke_board`) `DB_USER` | ConfigMap | `db.smoke.internal` 등 내부 이름 · 스키마는 `server/db/smoke_board.sql` |
| `DB_PASSWORD` | **Secret** | |
| `CHECK_TOKEN` | **Secret** | 16자 이상. Jenkins Credentials 의 같은 값으로 검증 API 호출 |
| `ADMIN_PASSWORD` | **Secret** | 없으면 공지 쓰기 로그인이 꺼진다 |
| `APP_SEED` | ConfigMap | 운영 `false` (이관 데이터 건수 보존) |

> 상태: Dockerfile 초안. 이 세션에서는 Docker Hub에 접근할 수 없어 이미지 빌드는 아직 실행하지 않았다.
