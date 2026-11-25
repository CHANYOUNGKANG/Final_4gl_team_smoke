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
