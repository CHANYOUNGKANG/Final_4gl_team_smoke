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

## 현재 현황 (2026-11-27)

| 범위 | 상태 | 증빙 |
| --- | --- | --- |
| CI 및 ECR | 레퍼런스 앱 자동 성공, 최종 JSP 호환 시험 성공 | [CI #6](verification/1127-notice-ci-build-6-auto.log) · [PR #21 시험](verification/1127-pr21-final-compatibility.log) |
| 정적 CD | EKS 후보 Green 갱신 성공 | [CD #4](verification/1127-notice-cd-build-4-deploy.log) |
| 정적 Blue/Green | 전환 20.23초, 복귀 21.56초, 연속 HTTP 341/341 성공 | [Release #5](verification/1127-notice-release-build-5-rollback.log) · [측정](verification/1127-alb-continuity-summary.md) |
| 동적 Plan | 활성 슬롯 자동 판별, 상위 CI에서 호출 성공 | [Handoff #2](verification/1127-notice-handoff-build-2.log) · [Plan #3](verification/1127-notice-plan-build-3-upstream.log) |
| 실제 JSP 앱 | PR #21 병합, 기존 H2/CRUD checker 성공 | [앱](../app/README.md) · [기존 레퍼런스](../app-reference/README.md) |
| 실제 운영 통합 | EFS 인계 완료 보고, RDS 및 동적 실제 CD/Release 대기 | [운영 준비](kubernetes/NOTICE-PROD.md) |

## 운영 안전선 및 남은 일

- 기존 `smoke-notice-cd` / `smoke-notice-release`는 정적 앱 실험 전용이며 수동 실행, 기존 성공 상태에서 반복 실행 금지.
- 기존 `smoke-notice-ci`의 Dockerfile 및 자동 호출 설정은 그대로 유지. main Poll SCM에 따른 빌드/ECR 등록은 기존 설정대로 발생할 수 있으나 배포·ALB 변경은 없음.
- 신규 [Dockerfile.prod-draft](docker/Dockerfile.prod-draft)는 숫자 UID/GID 1500:1500 및 EFS 경로 초안. 실제 빌드 전 정식 CI Dockerfile로 대체하지 않는다.
- [동적 Plan](jenkins/Jenkinsfile.notice-plan)은 읽기 전용, [렌더러](kubernetes/render-notice-prod.py)는 로컬 전용. 후보 배포 및 운영 트래픽 변경 권한을 부여하지 않는다.
- RDS boarddb, 앱 DML 계정, Secret(DB_PASSWORD/CHECK_TOKEN/ADMIN_KEY), 공용 PVC, /var/smoke/attach 연동 후 실제 앱 두 버전의 배포·검증·전환·롤백을 연결한다. 데이터 이관 전후 건수·해시 검증과 장애 시험은 별도.
- [작업일지](WORKLOG.md) · [이미지 색인](evidence/2026-11-27/README.md) · [요구사항](../docs/requirements/README.md) · [시연 기록표](../docs/delivery/README.md). PNG와 원본 CSV는 미등록. 실측 성공과 운영 완료 판정은 구분한다.

[PR #18](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/18) · [PR #19](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/19) · [PR #20](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/20) · [PR #21](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/21)
