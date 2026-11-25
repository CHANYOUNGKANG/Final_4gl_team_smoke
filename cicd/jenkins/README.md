# Jenkins · CICD1 첫 빌드

[CI/CD 파트](../README.md) · [작업일지](../WORKLOG.md) · [Jenkinsfile](Jenkinsfile) · [환경 값 예시](../config/deploy.env.example)

## 목적

GitHub `main`(또는 작업 브랜치)에 push하면 Jenkins가 같은 커밋으로 Maven 테스트를 돌리고 WAR를 만든다. 완료 기준은 **커밋 SHA · 테스트 결과 · WAR 경로와 해시가 한 빌드 로그에서 대조되는 것**이다 (이정표 CICD1).

## 대상 장비

| 장비 | 담당 | 확인할 값 | 상태 |
| --- | --- | --- | --- |
| Jenkins EC2 | 이우빈 생성 · 강찬영 설정 | OS, 인스턴스 유형, 접속 경로(Bastion/SSM), IAM 역할 | 인계 대기 |
| 공지 앱 소스 | 이준호 | `pom.xml` 위치, Java·Tomcat 버전, WAR 이름 | 인계 대기 ([app/README.md](../../app/README.md)) |
| GitHub 저장소 | 강찬영 | Webhook → `https://<Jenkins 주소>/github-webhook/` | Jenkins 준비 후 |

## 명령 근거

- **Jenkins는 Java 위에서 돈다.** 최신 LTS는 Java 17 이상이 필요하므로 21을 설치한다. 앱 빌드용 JDK는 이준호 인계값에 맞춰 따로 둘 수 있다.
- **Maven은 Jenkins 에이전트(이 EC2)에 있어야 한다.** Jenkinsfile은 `PATH`의 `mvn`을 쓴다.
- **저장소가 공개라 체크아웃에 토큰이 필요 없다.** GitHub 토큰을 만들지 않는 것이 가장 안전하다. 이후 AWS 접근은 EC2 IAM 역할로 하고 액세스 키를 만들지 않는다.

## 옵션 설명

| 설정 | 값 | 이유 |
| --- | --- | --- |
| 작업 유형 | Pipeline · *Pipeline script from SCM* | Jenkinsfile을 저장소에서 버전 관리 |
| Script Path | `cicd/jenkins/Jenkinsfile` | 파트 폴더 규칙 |
| Branch Specifier | `*/main` (테스트 때는 작업 브랜치) | |
| Build Triggers | *GitHub hook trigger for GITScm polling* | Jenkinsfile의 `githubPush()`와 같은 설정 |
| 플러그인 | Pipeline, Git, GitHub, JUnit, Timestamper | 기본 추천 플러그인에 대부분 포함 |
| 전역 환경 변수 | `APP_DIR` 등 ([예시](../config/deploy.env.example)) | 주소·계정 값을 코드에서 분리 |

**Credentials ID 규칙** — 코드에는 ID만 쓴다.

| ID | 종류 | 쓰는 단계 | 지금 필요 |
| --- | --- | --- | --- |
| *(없음)* | 공개 저장소 체크아웃 | CICD1 | — |
| `deploy-ssh` | SSH Username with private key | CICD3 Ansible → 배포 대상 | 아니오 |
| *(EC2 IAM 역할)* | ECR push · EKS · ALB · SNS | CICD2~4 | 아니오 · 키 대신 역할 |

## 성공 기준

1. 수동 *Build Now* 결과가 **SUCCESS**이고 콘솔에 `commit=<SHA>`, 테스트 요약, `target/*.war`, `sha256` 줄이 모두 보인다.
2. 작업 브랜치에 테스트 커밋을 push하면 **사람이 누르지 않아도** 빌드가 시작되고, 콘솔의 SHA가 GitHub 커밋 SHA와 같다.
3. 빌드 페이지에 *Test Result*와 WAR 아티팩트가 남는다.

→ 콘솔 로그를 `cicd/verification/build-<번호>.log`로 저장(주소·계정 가림)하고 `evidence.json`의 `CICD1.verification`에 등록.

## 문제 해결 순서

1. **Jenkins 화면이 안 열린다** → 서비스 상태 → 보안 그룹 8080 허용 출발지(관리자 IP만) → Bastion/SSM 경로
2. **`mvn: not found`** → EC2에 Maven 설치 여부, Jenkins 사용자 `PATH`
3. **`pom.xml` 없음** → 전역 변수 `APP_DIR`가 이준호 인계값과 같은지
4. **테스트 실패** → 로컬 같은 커밋에서 `mvn -B clean package` 재현, Java 버전 차이 확인
5. **push해도 빌드가 안 돈다** → GitHub Webhook *Recent Deliveries* 응답 코드 → 보안 그룹이 GitHub Webhook 출발지 대역을 허용하는지 → Build Triggers 체크

## 명령 모음 (Jenkins EC2, Amazon Linux 2023 기준 · OS 확정 후 재확인)

```bash
sudo dnf install -y java-21-amazon-corretto-devel git maven
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo dnf install -y jenkins
sudo systemctl enable --now jenkins
sudo systemctl status jenkins --no-pager
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
java -version
mvn -v
```

> `initialAdminPassword` 출력과 Jenkins 관리 화면 주소는 캡처·일지에 남기지 않는다. 저장소 키 파일 이름은 설치 시점의 [Jenkins 공식 설치 문서](https://www.jenkins.io/doc/book/installing/linux/)와 대조한다.
