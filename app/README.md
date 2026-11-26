# 공지 웹앱 인계표 · 해든정밀㈜ 공지·자료실

[서버 담당](../server/README.md) · [CI/CD 담당](../cicd/README.md) · [첫날 작업표](../docs/delivery/README.md#첫날-작업표) · [Docker 이미지](../cicd/docker/README.md)

> **시나리오**: ㈜스모크(수행사, 우리 팀)가 고객사 **해든정밀㈜**(가상의 정밀 가공 부품 제조사)의 공지·자료실을 넘겨받아, 보안을 재구축하고 AWS로 이전한 뒤 무중단으로 배포한다.
> 고객사가 쓰던 "기존 공지 앱"의 소스를 받지 못해서, 같은 기능을 가진 **레퍼런스 앱**을 이 폴더에 만들었다 (CI/CD 강찬영 작성, 11/26). 이준호가 실제 원본 앱을 넘기면 이 표를 그 앱 기준으로 다시 채운다.

| 항목 | 팀 확인값 |
| --- | --- |
| 소스 위치 · 기준 브랜치 또는 커밋 SHA | 이 폴더(`app/`) · `main`. 빌드 기준 커밋은 Jenkins 콘솔의 `commit=` 줄 |
| Java · Tomcat 버전 | Java 17 · Tomcat 10.1 (Spring Boot 3.3, Jakarta EE 10) |
| Maven 빌드 위치 · WAR 파일명 | `app/` 에서 `mvn -B -ntp clean package` → `app/target/notice.war` (Docker에서는 `ROOT.war`) |
| 공지 조회 경로 · 정상 응답에서 확인할 내용 | `GET /health` 200 + `"status":"UP"` · `GET /version` 의 `version`·`color`·`commit` · `GET /notices` 200 |
| 테스트 공지 작성·조회 방법 | `POST /api/check/notices` (헤더 `X-Check-Token`) → `GET /api/check/notices/{id}` → `DELETE` 로 정리. 검증 글은 고객 화면에 보이지 않음 |
| 필요한 환경 변수 이름 · 설정 주입 위치 | [Docker README의 표](../cicd/docker/README.md) — 비밀값 `DB_PASSWORD`·`CHECK_TOKEN`·`ADMIN_PASSWORD` 는 Kubernetes Secret / Jenkins Credentials |

첫 빌드의 완료 기준은 원본 커밋, Jenkins 테스트 결과, 생성된 WAR 경로를 한 실행에서 대조할 수 있는 것이다.

## 화면과 기능

| 경로 | 누가 | 내용 |
| --- | --- | --- |
| `/` | 누구나 | 최신 문서(도면 표제란 형태), 최근 공지 5건, 새 자료 4건, 검색 |
| `/notices` | 누구나 | 분류(공지·납품·물류·품질·인증·자료실) 탭, 제목·본문 검색, 고정 공지, 페이지 |
| `/notices/{id}` | 누구나 | 본문, 첨부 다운로드, 첨부별 SHA-256 |
| `/archive` | 누구나 | 모든 첨부 자료와 다운로드 수 |
| `/notices/new` | 관리자 | 공지 작성 + 다중 첨부 (파일당 20MB, 확장자 허용 목록) |
| `/health` `/version` | ALB·Probe·Jenkins | 상태 검사(DB·첨부 저장소) 200/503, 응답한 버전·슬롯 |
| `/api/check/notices` | Jenkins | 배포 검증용 숨김 글 작성·조회·삭제 (`CHECK_TOKEN` 없으면 404) |

모든 화면의 상단 막대와 하단 배지가 `DEPLOY_COLOR`(blue/green)로 바뀐다. ALB를 전환하면 같은 주소에서 색과 버전이 바뀌는 것으로 전환을 눈으로 확인할 수 있다.

## 블루그린·이관 요구사항과 연결

| 요구사항 | 앱에서 맞춘 것 |
| --- | --- |
| NFR-02 무중단 배포 | `/health` 가 DB·저장소까지 확인 → 준비 안 된 Pod는 대상 그룹에 안 들어감. `server.shutdown=graceful` 로 축소 시 진행 중 요청 처리 |
| SRS-REQ-03 공지 작성·조회 검사 | 검증 API가 응답에 `servedBy.version/color` 를 담아 “어느 버전이 처리했는지”를 로그로 남김 |
| NFR-03 데이터 무결성 | 첨부 업로드 시 SHA-256 저장 · 다운로드 응답 헤더 `X-Content-SHA256` · 대조 뷰 `v_migration_check` ([smoke_board.sql](../server/db/smoke_board.sql)) |
| NFR-04 보안 | 관리자 로그인은 `admin_user`의 bcrypt 해시로 확인, CSRF, CSP·X-Frame-Options, 업로드 확장자 허용 목록, UUID 저장 이름(경로 조작 차단) |
| 운영 데이터 보존 | `APP_SEED=false`(prod 기본) → 샘플 글을 넣지 않음, `DB_DDL=validate` → 앱이 테이블을 만들거나 바꾸지 않음 |

## 로컬 실행

```bash
cd app
mvn -B -ntp clean package                      # 테스트 포함
ADMIN_PASSWORD='로컬에서만-쓸-값' CHECK_TOKEN="$(openssl rand -hex 24)" DEPLOY_COLOR=blue \
  java -jar target/notice.war                  # http://localhost:8080  (H2 메모리 DB + 샘플 공지 7건)
curl -s localhost:8080/health
```

## 데이터베이스 — `smoke_board` (이준호 작성 · [server/db/smoke_board.sql](../server/db/smoke_board.sql))

앱은 이 스키마를 **그대로** 쓴다. 테이블·컬럼 이름과 분류 값(공지·납품일정·품질인증·도면)이 같고, 앱이 스키마를 바꾸지 않는다(`DB_DDL=validate`).

| 테이블 | 앱에서 쓰는 곳 |
| --- | --- |
| `notice` | 공지 목록·상세·작성. `is_check=1` 검증 글은 화면과 `v_migration_check` 건수에서 빠진다 |
| `attachment` | 첨부. `stored_name` = `UUID.확장자`, 실제 파일은 `APP_STORAGE_DIR`(NFS → 이관 후 S3) |
| `admin_user` | 직원 로그인 (bcrypt 해시) |

```bash
# 1) 데이터 서버에서 스키마 적용 ('비밀번호' 자리는 실행할 때만 바꾼다)
sudo mysql -u root -p < server/db/smoke_board.sql
# 2) 앱 실행 (운영 프로필)
SPRING_PROFILES_ACTIVE=prod DB_HOST=<데이터 서버> DB_USER=smoke DB_PASSWORD=<앱 계정 비밀번호> \
  ADMIN_PASSWORD=<첫 관리자 비밀번호> CHECK_TOKEN=<검증 토큰> java -jar target/notice.war
# 3) 확인
curl -s localhost:8080/health          # "db":"UP"
```

- 첫 관리자: `ADMIN_PASSWORD`를 주고 처음 켜면 `admin_user`에 `ADMIN_USERNAME`(기본 `admin`) 한 줄을 bcrypt 해시로 만든다. 이미 있으면 건드리지 않는다.
- CI(`App build` → `mariadb` 작업)가 매 PR마다 이 SQL을 MariaDB 10.11에 넣고 앱을 prod 프로필로 붙여 확인한다.

## 아직 안 한 것

- Redis 목록 캐시(장애 시 RDS 직조회), S3·CloudFront 첨부 제공 — 지금은 첨부를 파일 시스템(NFS·EFS)에서 제공한다. 이우빈과 범위 확정 후 추가.
- 실제 원본 앱이 있으면 이 레퍼런스 앱과 스키마 차이를 비교해야 한다 (이준호).
