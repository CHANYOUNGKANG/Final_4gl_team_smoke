# CI/CD 작업일지 · 강찬영

최신 항목이 맨 위. 항목마다 **확인한 결과(직접 실행·관찰한 것만) · 막힌 부분 · 다음 작업 · 증빙**을 남긴다. 캡처는 민감값을 가린 사본만 [evidence/](evidence/)에 둔다.

## 이정표 현황

| 이정표 | 내용 | 구현 | 실행 | 근거 |
| --- | --- | :---: | :---: | --- |
| CICD1 | Jenkins 테스트·WAR 빌드 | 초안 + 빌드 대상 앱 (PR #8) | Actions에서 같은 명령 통과 · Jenkins 미실행 | [jenkins/Jenkinsfile](jenkins/Jenkinsfile) · [app/](../app/) |
| CICD2 | Docker 이미지 · ECR 등록 | — | — | |
| CICD3 | Ansible Green 배포 · 상태 검사 | — | — | |
| CICD4 | 검증 후 전환 · 자동 롤백 | — | — | |

---

## 2026-11-26 (목) 15:00 · 빌드 대상 앱(해든정밀 공지·자료실)과 CI 빌드 검사 (PR #8)

**확인한 결과**
- 수행계획서상 ㈜스모크 = 수행사(우리 팀), 고객사는 이름 미정 → 가상 고객사 **해든정밀㈜**(정밀 가공 부품 제조)로 정함.
- `app/` 인계표 6항목이 모두 "확인 대기"였고 원본 앱 소스가 없어 CICD1이 빌드할 대상이 없었음 → Spring Boot 3.3 WAR 레퍼런스 앱을 `app/`에 작성.
- GitHub Actions `App build`(PR #8, 커밋 `6a87d7e`)에서 Jenkinsfile과 같은 `mvn -B -ntp clean package` 통과: 테스트 8건 성공, `target/notice.war` 생성.
- 같은 실행에서 WAR를 띄워 `/health` → `"status":"UP"`, `/notices` 200, 검증 API 작성→조회→무토큰 401→삭제 통과.
- 이 작업 환경에서는 Maven Central·Docker Hub 접근이 막혀 로컬 빌드·이미지 빌드는 하지 못함. 빌드 확인은 Actions 결과만 근거로 씀.

**막힌 부분 · 확인 필요**
- 이준호에게 원본 공지 앱이 실제로 있는지 확인 필요. 있으면 스키마 차이 비교 후 이 앱을 바꾸거나 맞춘다.
- Redis 캐시·S3/CloudFront 첨부 제공은 아직 없음(첨부는 NFS·EFS 경로) → 이우빈과 범위 결정.
- `cicd/docker/Dockerfile` 초안은 미빌드.

**다음 작업**
- Jenkins EC2(이우빈 인계) 준비되면 CICD1 실제 실행 → 콘솔의 `commit=`·테스트 결과·WAR SHA-256 캡처(가린 사본).
- CICD2: Dockerfile 빌드 → ECR push(태그 = 커밋 SHA 7자리).
- Jenkins Credentials에 `CHECK_TOKEN` 등록 → CICD3 검증 단계에서 `/api/check/notices` 호출.

**증빙** — PR #8 Actions `App build` 실행 요약(health JSON, WAR SHA-256)

---

## 2026-11-25 (수) 22:30 · 저장소 문서 자동화 · 설계 결정 정리 (PR #7)

**확인한 결과**
- `topology.json` → 구성도 SVG·IP 표 자동 생성이 기존 그림과 같은 결과를 냄 (로컬 실행).
- AWS VPC를 `10.0.0.0/16`으로 바꾸면 “대역 겹침”으로 생성이 실패함 → 기본 VPC 대역 실수를 PR에서 잡을 수 있음.
- 문서 링크 검사: 깨진 링크 2건은 모두 이 PR(#3)의 파일을 가리킴 → #3 병합 후 해소.

**이번 PR(#3)에 반영**
- 체크리스트의 “Webhook 연결”을 Poll SCM 기준으로 수정, `deploy.env.example`에 `EKS_ASG` 추가.

**CI/CD 관련 설계 기록** — [ADR-0003 단일 EKS 블루그린](../docs/decisions/0003-blue-green-single-eks.md), [ADR-0004 Poll SCM](../docs/decisions/0004-jenkins-poll-scm.md), [배포 롤백 런북](../docs/runbooks/deploy-rollback.md) (초안 · 미검증)

**다음 작업** — 병합 순서 #3 → #7(Update branch) → #5. 11/26 인계 이슈 2건(이준호 앱, 이우빈 EC2·SG·IAM).

---

## 2026-11-25 (수) 21:40 · IP 대역표 반영

**확인한 결과**
- 팀 대시보드의 IP 대역·통신 허용표가 최신화됨 → 공용 문서 `docs/architecture/ip-plan.md`로 옮김 (PR #4, 제안 값).
- CI/CD에 걸리는 값: Jenkins는 퍼블릭 서브넷 `10.100.1.0/24`, Jenkins SG는 8080·22를 **실습 PC 공인 IP/32만** 허용, Ansible EC2와 EKS 워커는 프라이빗 앱 `10.100.11·12.0/24`, ALB → Pod 포트 8080, Jenkins·Ansible → EKS API·ECR 443은 IAM 역할 + Access Entry.

**바꾼 것**
- Jenkinsfile 트리거: SG 때문에 GitHub Webhook이 도달할 수 없어 `pollSCM('H/2 * * * *')`를 기본으로 추가 (`githubPush()`는 SG에 GitHub hooks 대역을 열 때를 위해 유지).
- Jenkins README·`deploy.env.example`에 서브넷 배치와 SG 조건 반영.

**막힌 부분 · 확인 필요**
- Webhook을 쓸지(SG에 GitHub hooks 대역 추가) Poll SCM으로 갈지 이우빈과 결정.
- 대시보드의 DVWA 포트(`:8081` vs `-p 8080:80`) 불일치 — 강민서·이준호 확인.

**다음 작업** — 11/26 이우빈에게 Jenkins EC2·SG·IAM 역할(ECR push, EKS Access Entry) 인계 요청

---

## 2026-11-25 (수) · 저장소 점검과 CICD1 준비

**확인한 결과**
- `cicd/` 하위 폴더 5개(jenkins·docker·kubernetes·ansible·verification)는 `.gitkeep`만 있었다. 구현 파일 0개.
- 진행률 집계(Actions, main `19674de`) 기준 CI/CD **0/8점**, 팀 전체 0/32점.
- CI/CD 파트 PR·작업 브랜치 없음. `evidence.json` 비어 있음.
- [app/README.md](../app/README.md) 인계표 6개 항목 모두 “확인 대기” → 빌드할 소스 위치, Java·Tomcat 버전, WAR 이름이 정해지지 않았다.
- `aws/`에 파일 없음 → Jenkins EC2 접속 경로와 Webhook 수신 경로 미전달.
- 저장소 쪽 준비 완료: README 라이브 패널, 이슈 폼, 진행률 자동 집계. 보안 자동 검사(gitleaks·PR 검사)는 PR #2.

**막힌 부분**
- 앱 소스 (이준호 → 강찬영). 없으면 `mvn package` 자체를 돌릴 수 없다.
- Jenkins EC2 (이우빈 → 강찬영). 없으면 Jenkins 설치·Webhook 연결을 시작할 수 없다.
- 둘 다 11/26 첫날 작업표의 인계 항목이다.

**이번에 만든 것 (미실행)**
- [jenkins/Jenkinsfile](jenkins/Jenkinsfile): Source → `mvn -B -ntp clean package` → JUnit 결과 → WAR·sha256 보관. 비밀값 없음, `APP_DIR`는 전역 환경 변수.
- [jenkins/README.md](jenkins/README.md): 설치·Job 설정·Credentials ID 규칙·성공 기준·문제 해결 순서.
- [config/deploy.env.example](config/deploy.env.example): 주소·계정 값은 예시만. 실제 값은 Jenkins 전역 변수.

**다음 작업**
1. 11/26 오전: 이준호에게 앱 인계표 6항목, 이우빈에게 EC2 접속 경로·IAM 역할·보안 그룹(8080은 관리자 IP + GitHub Webhook 대역만) 받기 — 인계 이슈로 요청
2. EC2에 Java 21·Maven·Jenkins 설치 → Pipeline Job(`cicd/jenkins/Jenkinsfile`) 수동 빌드 SUCCESS
3. Webhook 연결 → 테스트 커밋 push → 콘솔 SHA = GitHub SHA 확인
4. 콘솔 로그를 가려서 `verification/build-<번호>.log`로 저장 → `evidence.json`에 CICD1 등록 → CICD1 2/2점
5. 이어서 Dockerfile(CICD2)

**증빙** — PR #2 (보안 자동 검사), 이 작업일지 PR
