# AWS 클라우드

![이우빈 · AWS 클라우드 · 이관](../docs/images/role-aws.svg)

**담당자 메일**　[woobin6318@gmail.com](mailto:woobin6318@gmail.com)　·　[프로젝트 홈](../README.md)　·　[요구사항](../docs/requirements/README.md)

두 가용 영역의 서비스 운영 기반을 만들고 데이터 이관과 장애 복구를 검증한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [infrastructure/](infrastructure/) | VPC·EKS·ALB, IAM·보안 그룹 및 대상 그룹 구성 |
| [migration/](migration/) | RDS·S3 이관 절차와 원본 대조 결과 |
| [operations/](operations/) | 전환·복귀 스크립트, 복구 시간과 실제 비용 기록 |

## 작업 체크리스트

- [ ] 예산·가동 시간을 합의하고 Jenkins EC2 접근 경로와 Webhook 수신 경로를 강찬영에게 전달한다.
- [ ] 두 AZ의 EKS와 HTTPS ALB를 준비하고 ECR 위치·대상 그룹·전환 및 복귀 절차를 강찬영과 대조한다.
- [ ] 원본 게시글과 첨부파일을 RDS·S3로 이관하고 이준호와 [이관 결과](migration/)를 검증한다.
- [ ] 워커 장애 영향·ASG 교체 시간, 백업 복원과 블루그린 중복 운영 비용을 [운영 기록](operations/)에 남긴다.

[첫날 작업표와 파트 간 인계](../docs/delivery/README.md#첫날-작업표) · [시연 결과 기록](../docs/delivery/README.md#결과-기록표) · [작업 양식](../docs/templates/README.md) · [작업 이슈 열기](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.yml) · [인계 요청](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=handoff.yml)

## 팀 연동

이준호와 이관을 대조하고, 강찬영과 ECR 저장소·EKS 대상·ALB 전환 및 복귀 절차를 연결한다.
