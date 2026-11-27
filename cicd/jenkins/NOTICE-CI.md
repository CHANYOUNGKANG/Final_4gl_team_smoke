# 실제 공지 앱 CI · smoke-notice-ci (수동 CI 및 SCM WAR 검증 완료)

기존 `smoke-cicd` Job은 그대로 둔다. 새 Job은 공지 레퍼런스 앱(`app/`) 전용이며 EKS/ALB를 변경하지 않는다.

## Jenkins EC2 (Ubuntu 24.04, root 또는 ubuntu)

```bash
sudo apt-get install -y openjdk-17-jdk-headless
sudo -u jenkins -H /usr/lib/jvm/java-17-openjdk-amd64/bin/java -version
```

Jenkins 서비스 Java 21 및 기본 java alternatives는 유지한다. 파이프라인의 Java 17 경로만 별도로 설정한다. 설치 과정에서 기본 java가 바뀌었는지 확인하되 Jenkins 서비스 설정은 변경하지 않는다.

## 새 Job

| 항목 | 값 |
| --- | --- |
| Name | smoke-notice-ci |
| Type | Pipeline |
| Definition | Pipeline script from SCM |
| SCM | Git |
| Repository | https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke.git |
| Branch | */cicd/notice-ci-integration (첫 검증용, 병합 후 */main) |
| Script Path | cicd/jenkins/Jenkinsfile.notice-ci |
| Poll SCM | H/2 * * * * (Jenkinsfile에 선언) |

첫 실행은 WAR 및 JUnit 검증만 수행한다. Docker/ECR 파라미터 기본값은 false. 다음 실행에 `NOTICE_DOCKER_CHECK=true`로 격리된 H2 기동 검사, 그 성공 확인 후 두 파라미터를 true로 실행하면 ECR 등록까지 진행한다. 기존 SMOKE_AWS_REGION/SMOKE_ECR_REPO 사용. 태그는 notice-전체SHA-빌드번호로 test-SHA와 분리. Jenkins가 main을 감시하도록 바꾼 뒤에만 이 작업 브랜치를 정리한다.

## 2026-11-27 Build #5 · 자동 실행 확인

사용자 제공 Jenkins 상태 화면: 10:41:11 KST, Started by an SCM change, SUCCESS, 31초, revision `2f15d724a9067c8af348867a2861f50c45dfa83a`, notice.war 56.38 MiB 및 war.sha256 보관, 테스트 실패 없음. Docker/ECR 아티팩트는 확인되지 않아 자동 ECR 성공으로 판정하지 않는다.

## 자동 ECR 등록 옵션 (코드 반영, 실행 검증 대기)

Jenkins 관리 → System → Global properties → Environment variables에 `NOTICE_AUTO_PUBLISH=true`를 추가하면 SCM 변경으로 시작된 smoke-notice-ci Job에서 Docker H2 검사와 ECR 등록을 활성화한다. 기본 미설정/false는 기존 WAR-only 자동 실행 유지. 허용 브랜치는 main 및 cicd/notice-ci-integration이며 수동 빌드의 기존 두 체크박스는 유지한다. 실제 배포나 ALB 변경은 수행하지 않는다. 로그 `NOTICE CI MODE: scm=true autoPublish=true docker=true ecr=true` 및 `NOTICE ECR PUSH VERIFIED`, notice-ecr-image.txt 아티팩트로 확인한다. 매 SCM 변경(문서 변경 포함) 시 이미지가 생성될 수 있어 실습 종료 시 false로 변경하거나 main의 빌드 대상 경로 필터를 별도 설계한다.

## 완료 기준

- Java 17 및 Maven, 테스트 실패 0, notice.war 및 SHA-256 아티팩트.
- Docker: Tomcat /health 200, DB/storage UP, commit 일치 (H2 격리 시험만).
- ECR: push digest와 원격 조회 digest 일치.
- 실제 MariaDB/RDS, EFS, EKS, ALB, Blue/Green 전환은 별도 검증. [인계 이슈 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11).
- 작은 Jenkins 인스턴스에서 두 Job 동시 빌드를 피하고 디스크/메모리 상태를 확인한다. Docker 검사 시 운영 DB 변수/Secret을 전달하지 않는다.
