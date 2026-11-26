# CI/CD · 블루그린 배포

![강찬영 · CI/CD · 블루그린 배포](../docs/images/role-cicd.svg)

**담당자 메일**　[chanyoungcplus@gmail.com](mailto:chanyoungcplus@gmail.com)　·　[프로젝트 홈](../README.md)　·　[요구사항](../docs/requirements/README.md)

커밋 하나가 어떤 이미지로 배포됐는지 추적하고, 후보 기능 검사와 운영 전환·자동 복귀를 Jenkins로 연결한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [jenkins/](jenkins/) | Jenkins 파이프라인 설정·빌드 기록 |
| [docker/](docker/) | WAR 실행 이미지의 Dockerfile·빌드 컨텍스트 |
| [kubernetes/](kubernetes/) | Blue·Green Deployment, Service, readiness probe |
| [ansible/](ansible/) | 후보 배포·검증 및 트래픽 전환 호출 플레이북 |
| [verification/](verification/) | 빌드·배포 로그, 전환 전 차단·자동 롤백 측정 결과 |
| [evidence/](evidence/) | 가린 캡처와 “무엇을 증명하는지” 색인 |
| [config/](config/) | 환경 값 예시(`*.example`) — 실제 값은 Jenkins 전역 변수 |

**작업일지** [WORKLOG.md](WORKLOG.md) · **Jenkins 설정** [jenkins/README.md](jenkins/README.md)

## 현재 현황 (2026-11-26)

테스트 환경: Jenkins 수동·SCM 자동 WAR 빌드, Docker 이미지 생성, Tomcat HTTP 200, ECR 자동 Push 및 Digest 검증 성공. [Build #5 증빙](verification/smoke-test-build-5-ecr.log) · [작업일지](WORKLOG.md). 실제 공지 앱 통합은 미검증이며 공식 이정표 점수와 구분한다. [Ansible/EKS 인계 및 블루그린 협의안](ansible/HANDOFF.md)은 아직 구현 전이다.

Jenkins 서비스 계정 → Ansible 배포 계정 SSH 및 원격 Ansible ping/AWS STS 인증 성공. [실행 관찰 기록](verification/ansible-remote-check.log). Jenkins Job 원격 플레이북 검사는 Build #8에서 6개 작업 모두 성공했다. [Build #8](verification/smoke-test-build-8-ansible.log). EKS 배포는 아직 미검증이다. 활성화하려면 Jenkins 환경 변수 `SMOKE_ANSIBLE_HOST`(실제 주소 비공개), `SMOKE_ANSIBLE_CHECK=true`를 설정한다.

초기 Blue/Green 배포 코드는 [Kubernetes 실행 가이드](kubernetes/README.md) 및 [초기 배포 플레이북](ansible/bootstrap-smoke.yml)에 작성했다. 기본값은 서버 dry-run이며 실제 EKS 배포 및 ALB 전환은 자동 실행하지 않는다.

## 작업 체크리스트

- [ ] 이준호에게 [앱 빌드 정보](../app/README.md)를 받고 이우빈과 Jenkins EC2(퍼블릭 서브넷)·SG(실습 PC IP/32)·IAM 역할을 확인한다.
- [ ] EC2의 Jenkins에 팀 저장소를 연결하고 Maven 테스트와 WAR 빌드를 수동으로 성공시킨다.
- [ ] Poll SCM 자동 빌드([ADR-0004](../docs/decisions/0004-jenkins-poll-scm.md)) 확인 후 테스트 커밋을 push한다. Jenkins 로그의 SHA, 테스트 실행 결과, WAR 경로를 남긴다.
- [ ] WAR를 Docker 이미지로 만들어 실행·조회한 뒤 커밋 SHA 태그로 ECR에 올린다.
- [ ] [Kubernetes](kubernetes/)에서 Blue·Green Deployment, Service, readiness probe와 Green 전용 검사 경로를 준비한다.
- [ ] [Ansible](ansible/)로 Green을 배포하고 게시글 작성·조회를 검사한다. 실패하면 Blue가 운영 요청을 계속 받는지 확인한다.
- [ ] 검사 통과 시 이우빈의 ALB 전환 절차를 Jenkins에서 호출한다. 운영 주소 검사 실패 시 Blue 자동 복귀와 이전 버전 응답을 확인한다.
- [ ] Jenkins 결과를 SNS로 보내고 운영 메일 수신을 이준호와 확인한다. [검증 기록](verification/)에 연속 조회 실패 수와 복귀 시간을 남긴다.

[첫날 작업표와 파트 간 인계](../docs/delivery/README.md#첫날-작업표) · [시연 결과 기록](../docs/delivery/README.md#결과-기록표) · [작업 양식](../docs/templates/README.md) · [작업 이슈 열기](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.yml) · [인계 요청](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=handoff.yml)

## 팀 연동

첫 연동은 GitHub push → Jenkins → Maven 테스트·WAR 생성이다. 이후 ECR 푸시, Green 배포, 기능 검사, ALB 전환과 결과 알림을 연결한다.

[CI/CD 담당 체크리스트 원본 화면](../docs/images/cicd-checklist.png) · [블루그린 설계](../docs/architecture/README.md)
