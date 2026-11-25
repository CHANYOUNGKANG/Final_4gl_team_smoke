# CI/CD · 블루그린 배포

**담당 강찬영** · [프로젝트 홈](../README.md) · [요구사항](../docs/requirements/README.md)

커밋 하나가 어떤 이미지로 배포됐는지 추적하고, 후보 기능 검사와 운영 전환·자동 복귀를 Jenkins로 연결한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [jenkins/](jenkins/) | Jenkins 파이프라인 설정·빌드 기록 |
| [docker/](docker/) | WAR 실행 이미지의 Dockerfile·빌드 컨텍스트 |
| [kubernetes/](kubernetes/) | Blue·Green Deployment, Service, readiness probe |
| [ansible/](ansible/) | 후보 배포·검증 및 트래픽 전환 호출 플레이북 |
| [verification/](verification/) | 전환 전 차단·전환 후 자동 롤백 측정 결과 |

## 팀 연동

첫 연동은 GitHub push → Jenkins → Maven 테스트·WAR 생성이다. 이후 ECR 푸시, Green 배포, 기능 검사, ALB 전환과 결과 알림을 연결한다.

[CI/CD 담당 체크리스트 원본 화면](../docs/images/cicd-checklist.png) · [블루그린 설계](../docs/architecture/README.md)
