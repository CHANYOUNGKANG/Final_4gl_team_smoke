# AWS 클라우드

**담당 이우빈** · [프로젝트 홈](../README.md) · [요구사항](../docs/requirements/README.md)

두 가용 영역의 서비스 운영 기반을 만들고 데이터 이관과 장애 복구를 검증한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [infrastructure/](infrastructure/) | VPC·EKS·ALB, IAM·보안 그룹 및 대상 그룹 구성 |
| [migration/](migration/) | RDS·S3 이관 절차와 원본 대조 결과 |
| [operations/](operations/) | 전환·복귀 스크립트, 복구 시간과 실제 비용 기록 |

## 팀 연동

이준호와 이관을 대조하고, 강찬영과 ECR 저장소·EKS 대상·ALB 전환 및 복귀 절차를 연결한다.
