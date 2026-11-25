# 작업 양식 모음

[프로젝트 홈](../../README.md) · [진행률 산정 기준](../progress/README.md)

복사해서 **내 파트 폴더**에 넣고 채우는 출발점이다. 이 폴더(`docs/templates/`)는 진행률 집계 대상이 아니므로, 여기 있는 예시가 점수로 잡히지 않는다. 실제 환경 값으로 바꿔 파트 폴더에 커밋해야 점수가 오른다.

| 파트 | 양식 | 복사할 위치 | 관련 이정표 |
| --- | --- | --- | --- |
| 네트워크 | [VLAN·IP 계획표](network/ip-plan.md) | `network/topology/` | NET1 |
| 네트워크 | [허용·차단 매트릭스](network/access-matrix.md) | `network/policies/` | NET2·NET3 |
| 네트워크 | [절체·차단 검증 기록](network/verification-log.md) | `network/verification/` | NET1–4 실행 |
| 서버 | [백업·원본 목록 보고서](server/backup-report.md) | `server/backup/` | SRV2 |
| 서버 | [운영 메일 수신 기록](server/mail-receipt-log.md) | `server/mail/` | SRV4 실행 |
| AWS | [이관 대조표](aws/migration-compare.md) | `aws/migration/` | AWS3 실행 |
| AWS | [워커 장애·복구 측정](aws/failover-measure.md) | `aws/operations/` | AWS4 실행 |
| AWS | [비용 기록](aws/cost-log.md) | `aws/operations/` | NFR-07 |
| CI/CD | [Jenkinsfile 출발점](cicd/Jenkinsfile.example) | `cicd/jenkins/Jenkinsfile` | CICD1 |
| CI/CD | [Dockerfile 출발점](cicd/Dockerfile.example) | `cicd/docker/Dockerfile` | CICD2 |
| CI/CD | [Blue·Green 매니페스트](cicd/notice-deploy.yaml.example) | `cicd/kubernetes/` | CICD3 |
| CI/CD | [배포·전환 측정 기록](cicd/release-measure.md) | `cicd/verification/` | CICD1–4 실행 |
| 공통 | [일일 기록](../daily/TEMPLATE.md) | `docs/daily/MMDD.md` | — |

**넣지 말 것**　비밀번호, 개인 키(`.pem`), 액세스 키, 계정 ID 원문. 필요한 값은 이름과 위치만 적는다.
