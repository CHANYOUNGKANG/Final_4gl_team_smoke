# CI/CD 작업일지 · 강찬영

최신 항목이 맨 위. 항목마다 **확인한 결과(직접 실행·관찰한 것만) · 막힌 부분 · 다음 작업 · 증빙**을 남긴다. 캡처는 민감값을 가린 사본만 [evidence/](evidence/)에 둔다.

## 이정표 현황

| 이정표 | 내용 | 구현 | 실행 | 근거 |
| --- | --- | :---: | :---: | --- |
| CICD1 | Jenkins 테스트·WAR 빌드 | 초안 (PR) | — | [jenkins/Jenkinsfile](jenkins/Jenkinsfile) |
| CICD2 | Docker 이미지 · ECR 등록 | — | — | |
| CICD3 | Ansible Green 배포 · 상태 검사 | — | — | |
| CICD4 | 검증 후 전환 · 자동 롤백 | — | — | |

---

## 2026-11-26 · 테스트 WAR 수동 빌드 성공

**확인한 결과** — 사용자 제공 Jenkins 콘솔에서 Build #1, checkout SHA `53c07cb3fb098d868e8eff0fe311e65bfcfd18a8`, Maven 13.930초, JUnit 1건 통과, WAR 1608 bytes, 아티팩트 보관 및 fingerprint, Finished: SUCCESS 확인 (12:10:11 KST). Ubuntu 24.04.5 LTS x86_64, Java 21, Maven 3.8.7, Git 2.43.0, Swap 2 GiB, Jenkins 2.580.3. 플러그인 미러 연결 시간 초과는 공식 Plugin Manager 및 대체 아카이브 서버를 이용해 필수 플러그인을 복구했다.

**막힌 부분** — 실제 공지 앱 미인계. 마지막 요약의 commit=null은 명시적 Git SHA 환경 변수로 수정했다(실행 확인 전). 테스트 WAR 성공은 실제 공지 앱 인수 검증과 구분한다.

**다음 작업** — test-v2 변경을 Poll SCM이 감지하는지 확인 후 Docker/ECR 연동. ECR 저장소 및 IAM 권한 인계 필요.

**증빙** — [Build #1 발췌](verification/smoke-test-build-1.log).

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
