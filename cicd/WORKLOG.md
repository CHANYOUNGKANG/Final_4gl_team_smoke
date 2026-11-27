# CI/CD 작업일지 · 강찬영

최신 항목이 맨 위. 항목마다 **확인한 결과(직접 실행·관찰한 것만) · 막힌 부분 · 다음 작업 · 증빙**을 남긴다. 캡처는 민감값을 가린 사본만 [evidence/](evidence/)에 둔다.

## 이정표 현황

| 이정표 | 내용 | 구현 | 실행 | 근거 |
| --- | --- | :---: | :---: | --- |
| CICD1 | Jenkins 테스트·WAR 빌드 | 테스트 파이프라인 및 레퍼런스 앱 | 실제 공지 앱 Jenkins 수동 #1~3 성공 · SCM 자동 실행 검증 대기 | [Build #5](verification/smoke-test-build-5-ecr.log) · [App build](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/runs/45773618799) |
| CICD2 | Docker 이미지 · ECR 등록 | 테스트 이미지 자동 Push 구현 | 실제 앱 Docker H2/ECR Push 검증 성공 | [Build #5](verification/smoke-test-build-5-ecr.log) |
| CICD3 | Ansible Green 배포 · 상태 검사 | 초기 매니페스트·플레이북 작성 | 정적 앱 EKS 초기 배포·HTTP 200·Jenkins 원격 조회 성공; 실제 후보 CD 대기 | [Build #8](verification/smoke-test-build-8-ansible.log) |
| CICD4 | 검증 후 전환 · 자동 롤백 | — | — | |

---

## 2026-11-27 10:35 KST · DAY 2 중간 저장

**확인한 결과** — 실제 공지 앱 Jenkins #1~3 수동 실행 SUCCESS, Java 17, JUnit 10/10, Docker H2 및 ECR Push/Digest 검증. Ansible → EKS Private API, namespace RBAC, 정적 테스트 앱 Blue/Green create-only 배포(2 Deployment, 2 Service, 4 Pod Running, 두 워커 분산), Port Forward 권한 수정 후 HTTP 200 test-v2/test-v3, Jenkins 서비스 계정 원격 조회 성공.

**막힌 부분** — 실제 업무 앱의 SCM 자동 실행 및 ECR 자동 실행 검증, RDS/EFS, 실제 후보 업데이트 CD, ALB 전환·자동 복귀 미검증. AZ 라벨 별도 확인. 기존 리소스 재생성 금지. PR #13은 중간 저장 Draft로 유지한다.

**증빙** — [DAY 2 상세 관찰 기록](verification/1127-day2-midpoint.md) · [Build #1](verification/1127-notice-ci-build-1.log) · [Build #2](verification/1127-notice-ci-build-2.log) · [Build #3](verification/1127-notice-ci-build-3.log). 마스킹 캡처 PDF/ZIP 별도 준비, 바이너리 업로드 대기.

---

## 2026-11-26 · 팀 앱과 CI/CD 작업 통합 (PR #12)

**확인한 결과** — PR #10(DB), #8(레퍼런스 공지 앱), #9(회사 소개) main 병합 확인. [App build](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/runs/45773618799) build 및 mariadb 작업 성공 확인. 정적 테스트 앱의 Jenkins Build #8 증빙과 실제 공지 앱 Actions 증빙은 구분한다.

**막힌 부분** — 실제 공지 앱 Jenkins 빌드 및 ECR 이미지 검증, EKS/ALB 연동, DB 주소 확정은 미완료. [인계 이슈 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11) 참조.

**다음 작업** — 기존 smoke-cicd Job/브랜치 유지. main 기반 공지 앱용 별도 Job에서 Java 17/WAR 빌드부터 확인. EKS 초기 매니페스트는 테스트 앱 전용이며 자동 운영 배포 금지.

---

## 2026-11-26 (목) 16:30 · 앱을 이준호 DB 스키마(smoke_board)에 맞춤 (PR #8, #10)

**확인한 결과**
- 이준호 `server/db/smoke_board.sql`을 PR #10으로 올림(내용 그대로).
- 앱 테이블·컬럼·분류 값을 이 스키마와 같게 바꾸고, 관리자 로그인을 `admin_user`(bcrypt)로 변경.
- Actions `App build` → `mariadb` 작업(커밋 `540ee16`): MariaDB 10.11에 SQL 적용 → 분류별 2건씩 8건, 앱을 prod 프로필(스키마 검증)로 기동 → `/health` `"db":"UP"`, 샘플 글·도면 분류 조회, 검증 글 `is_check=1`로 저장되고 `v_migration_check` 건수 8 유지, 관리자 bcrypt 1건 생성 확인. 단위 테스트 10건 통과.

**막힌 부분 · 확인 필요**
- SQL의 서버 주소(`10.10.40.10`, 앱 계정 `10.10.30.%`)와 `docs/architecture/ip-plan.md`(`10.0.40.10`, `10.0.30.0/24`)가 다름 → 강민서·이준호 확인. CI는 별도 CI 전용 계정으로 확인함.

**다음 작업** — 병합 순서 #10 → #8 → #9. Jenkins EC2 준비되면 CICD1 실제 실행.

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

## 2026-11-26 16:14 KST · Build #8 Ansible까지 자동 연동 성공

**확인한 결과** — SCM 변경 자동 감지, Git SHA `97861a363d9ff5a483b94cd5407b21d5ebd60c3b`, Maven 3.465초, JUnit 1건 통과, WAR 및 Docker linux/amd64 이미지, HTTP 200, ECR Push 및 Digest 검증, Jenkins Job에서 원격 Ansible 플레이북 6개 작업 성공(ok=6 changed=0 failed=0 skipped=0), 배포 계정 및 IAM 역할 검사 성공. 16:14:10~16:14:31 KST 로그 구간 약 21초. Build #7에서 Ansible when 조건으로 생략된 문제는 Build #8에서 해결됨.

**막힌 부분** — EKS 클러스터·버전·Access Entry/RBAC 및 실제 공지 앱 인계 대기. ALB 제어 방식 및 대상 그룹 미확정. EKS 배포/트래픽 전환 실적은 아직 없음.

**이번에 작성한 것 (실행 전)** — [초기 Blue/Green 매니페스트](kubernetes/notice-slot.yaml.j2), [Ansible 초기 배포](ansible/bootstrap-smoke.yml), [변수 예시](config/bootstrap-smoke.vars.example.yml), [실행 가이드](kubernetes/README.md). 기본 server dry-run, 명시적 승인 시 create-only. 기존 자동 CI 파이프라인에 EKS 배포를 연결하지 않음. 초기 자원 수치는 제안값. ALB 전환과 후보 업데이트는 실제 트래픽 상태를 확인한 뒤 별도 구현한다.

**증빙** — [Build #8 정제 로그](verification/smoke-test-build-8-ansible.log).

---

## 2026-11-26 · Ansible EC2 인계 및 Jenkins 원격 실행 검증

**확인한 결과** — 사용자 제공 터미널 화면: Jenkins에서 Ansible 사설 SSH 22 통신 성공, SSH Gateway 접속 성공. Ubuntu 24.04.5 LTS x86_64, 호스트명 smoke-ansible, KST, RAM 909MiB, Swap 2GiB, 루트 파일시스템 약 14G. Ansible Core 2.16.3, Python 3.12.3, Git 2.43.0, AWS CLI 2.42.4 설치 및 localhost ping 성공. ansadmin 계정과 /opt/devops 생성, Jenkins 전용 ED25519 공개키 등록 및 호스트 지문 대조, BatchMode=yes/StrictHostKeyChecking=yes 무인 SSH 성공. Jenkins 서비스 계정에서 원격 Ansible ping SUCCESS/pong 및 AWS STS assumed-role smoke-ansible-role 확인.

**막힌 부분** — eks:ListClusters AccessDenied (필수 배포 권한은 아님). 실제 클러스터명·버전, eks:DescribeCluster, Access Entry 및 RBAC 검증 대기. Jenkins Job 자체에서 원격 플레이북 실행은 아직 미검증. 실제 공지 앱 및 ALB 전환도 미검증.

**다음 작업** — 테스트 전용 원격 플레이북을 추가하고 Jenkins 환경 변수 SMOKE_ANSIBLE_HOST 및 SMOKE_ANSIBLE_CHECK=true를 설정한 뒤 실행 검증한다. 기본 비활성화. EKS 리소스를 변경하지 않으며 실제 관리 주소·키·계정 식별자는 저장소에 기록하지 않는다.

**증빙** — [Ansible 원격 실행 관찰 기록](verification/ansible-remote-check.log).

---

## 2026-11-26 14:11 KST · ECR 자동 Push 검증 완료 및 CD 인계 설계

**확인한 결과** — 사용자 제공 Build #5 전체 콘솔에서 SCM 변경 자동 실행, SHA `32233749f3ae7ebf9cbc03b1b4d58ca6bb17a4b1`, JUnit 1건 통과/실패 0건, Maven 3.799초, Tomcat HTTP 200, ECR 자동 로그인·Push 및 Digest 대조, ecr-image.txt 및 WAR·SHA-256 아티팩트 보관, 12:26:27 KST SUCCESS 확인. 별도 ECR 조회 화면에서도 동일 태그와 Digest 확인. 12:26:09~12:26:27 로그 구간 약 18초.

**막힌 부분** — 실제 공지 앱 인계표 미확정. Ansible EC2, EKS, IAM Access Entry, ALB 전환 방식은 구축 확인 전. 관리 인증 강화 및 최소 권한 검증도 남음. 테스트용 정적 WAR의 성공을 실제 앱 통합이나 무중단 배포 성공으로 간주하지 않는다.

**다음 작업** — [Ansible/EKS 인계 및 블루그린 협의안](ansible/HANDOFF.md)에 우빈 씨와 합의할 EC2·SG·IAM·Kubernetes·ALB 조건을 정리했다. Ansible 접속 검증 → 후보 배포 및 상태 검사 → 전환·복귀 및 연속 요청 실측 순서로 작업. 실제 앱 인계 후 별도 검증.

**증빙** — [Build #5 콘솔 발췌 및 ECR 조회](verification/smoke-test-build-5-ecr.log).

---

## 2026-11-26 · Docker 자동 빌드 및 ECR 수동 Push 성공

**확인한 결과** — Jenkins 사용자 hello-world 성공. Build #3 사용자 제공 콘솔: SCM 자동 실행, SHA `7683373495abb6cfab7cbb2df46339cb2d83bb01`, JUnit 1건 통과, Maven 4.307초, linux/amd64 이미지 생성, Tomcat 10.1.62 기반 HTTP 200, 아티팩트 보관, SUCCESS (12:20:41 KST). AWS CLI 2.42.4, EC2 IAM 역할 기반 STS 인증과 ECR 조회 성공. 사용자 제공 화면에서 12:22:36 KST 테스트 이미지 수동 Push 및 ECR 조회 digest 일치 확인.

**막힌 부분** — 실제 공지 앱 인계 및 ECR 자동 Push 실행 검증 전. 관리 인증 강화와 IAM 최소 권한 확인 필요.

**다음 작업** — ECR 자동 Push 단계는 기본 비활성화. 관리 인증 강화 후 Jenkins 환경 변수로 명시적으로 켜고 실제 자동 Push와 digest 대조를 검증한다. 운영 태그와 분리된 test-SHA만 사용한다.

**증빙** — [Build #3 및 ECR 수동 Push 발췌](verification/smoke-test-build-3-ecr.log).

---

## 2026-11-26 · Poll SCM 자동 빌드 성공 및 Docker 기반 준비

**확인한 결과** — 사용자 제공 Jenkins Build #2 화면: 12:14:09 KST, Started by an SCM change, revision `efd84d33bbbabfed4e114707147127468e1b489c`, SUCCESS, 소요 12초, WAR 및 해시 아티팩트, 테스트 실패 없음. Docker Engine 29.10.1, Buildx 0.39.1, 서비스 active 및 root hello-world 성공. Jenkins docker 그룹 등록, Jenkins 재시작, Jenkins 사용자 docker ps 정상.

**막힌 부분** — Jenkins 사용자 hello-world 재확인 및 이미지 빌드 실행 결과 미확인. 실제 앱과 ECR URI·IAM 인계 대기.

**다음 작업** — 테스트 전용 Dockerfile과 이미지 빌드/HTTP 검사 스테이지 추가. ECR에 아직 push하지 않는다. 실제 앱의 Tomcat 버전은 서버 담당자와 별도 합의. Docker 그룹은 root 수준 권한이므로 신뢰된 브랜치만 빌드하고 관리 접속 및 IAM 권한을 제한한다.

**증빙** — [Build #2 화면 관찰 기록](verification/smoke-test-build-2.log).

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
