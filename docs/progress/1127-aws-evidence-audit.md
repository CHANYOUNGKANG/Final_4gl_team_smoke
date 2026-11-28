# DAY 2 AWS 증빙 재감사 · 2026-11-27 수행 / 2026-11-28 재평가

## 후속 추가 근거 — DAY2 사용자 실행 결과 회수

아래 본문은 main 2f5ce3a를 기준으로 실시한 **3/8 판정 당시의 감사 이력**이다. 이후 AWS 담당의 DAY2 재게시 과정에서 실제 사용자 명령·출력과 원본 대조가 추가됐으므로 현재 상태는 이 후속 절과 [최신 AWS 작업일지](../../aws/WORKLOG.md), [진행률 근거](evidence.json)를 함께 따른다. 기존 감사의 관찰·팀원 기록은 삭제하지 않았다.

- **AWS1:** 11/27 09:17:41 사용자 조회에서 두 노드 Ready, 각각 ap-northeast-2a/2c가 회수됐다. [구성·접근 기록](../../aws/infrastructure/1127-eks-access-and-controller.md)과 [출처 표시 발췌](../../aws/verification/1127-recovered-user-results.log)에 연결해 2/2로 등록했다.
- **AWS2:** 기존 HTTP ALB·가중치·대상 그룹의 부분 구현 1/2를 유지한다. HTTPS·인증서·실제 업무 앱 통합은 여전히 별도다.
- **AWS3:** 실제 RDS 복원·스키마 명령과 exit0, 14/1/6 및 두 digest, EFS 두 AZ와 S3의 첨부 해시, S3 익명403을 회수했다. 실제 14:04 인계 압축파일 내부 값·JPG189,525bytes의 새 해시 계산과 대조해 2/2로 등록했다. [전체 대조·명령·한계](../../aws/migration/1127-source-and-target-evidence.md). 서버의 다른 시점 14/1/2 복구 화면을 RDS 기준으로 바꾸지 않았다.
- **AWS4:** 워커 장애·교체·모니터링 실측은 없으므로 0/2를 유지한다.

기존 report.py의 로컬 실행 결과는 **AWS5/8(62.5%), 팀19/32(59.4%)**다. 원격 검사·main 반영은 새 PR과 [Issue #1](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1)에서 확인한다. 원문 전체나 새 AWS 재실행으로 격상하지 않고 검색이 반환한 USER 출력·요약의 범위를 명시했다. CronJob은 수동 Job 완료와 달리 suspend=True이며 자동 실행 완료가 아니다.

---

## 3/8 감사 이력 (후속 근거 회수 전)

기준 main: `2f5ce3a`. 관련 #1, #11, #29, PR #27(병합), #30(병합), #28(병합), #25(열린 draft), #26(열림). 본 문서는 저장소 증빙 감사이며 AWS 계정에 새로 접속한 실측이 아니다. 11/28 게시한 11/27 캡처를 실제 수행일에 귀속한다.

## 결론

- 기존 공식 0/8은 전체 이정표 충족 및 근거 등록 여부를 나타냈으나, 실제 구현한 구성까지 0으로 보이는 문제가 있다.
- 공통 0/1/2 체계의 1점은 실제 핵심 구현(부분 구축 인정, 설계만으로 불가), 2점은 전체 이정표의 인수 검증으로 명확화한다. 점수 코드의 계산식이나 정규식은 변경하지 않는다.
- AWS1 1/2, AWS2 1/2, AWS3 1/2, AWS4 0/2 = **3/8 (37.5%)**. 다른 파트의 기존 점수는 이 AWS 감사에서 변경하지 않는다. 기존 14/32에 3점을 더하면 17/32(53.1%) 예상. 자동 Actions 실제 계산 확인과 병합 후 게시 필요.
- 작업량과 남은 시간의 비율이 아니라 이정표 기반 점수이다. 이전 AWS 작업일지의 0/8은 당시 채점 결과로 보존한다.

## 증거 분류

A: 공개용 PNG를 직접 시각 확인하거나 실제 CLI/콘솔 발췌에서 확인. B: 팀원의 화면 관찰 전사·로그 요약 또는 원본과의 대조 보고. C: 담당자 완료 보고만 존재하여 대상 실행 원문 미확보. D: 미완료 또는 미검증. A/B도 라이브 환경 재실행이나 진위 독립 인증을 의미하지 않는다. 화면에서 가린 식별자는 추정하지 않는다.

## 11/26 기반 캡처 전수 (7장)

| 파일 | 직접 확인 및 범위 |
| --- | --- |
| [VPC](../../aws/evidence/1126-vpc-map-masked.png) | A: 서울 2a/c, public/app/data 6개, RT 4개, IGW와 NAT 연결. NAT 2개가 아님 |
| [서브넷](../../aws/evidence/1126-subnets-masked.png) | A: 6개 Available |
| [SG](../../aws/evidence/1126-security-groups-masked.png) | A: EFS/RDS/Ansible/ALB/Redis/Jenkins/Bastion 이름 존재. 실제 개별 규칙이나 Redis 인스턴스 생성은 별도 |
| [SSH](../../aws/evidence/1126-ansible-ssh-rule-masked.png) | A: Ansible SG SSH TCP22; 출발지는 마스킹 |
| [아웃바운드](../../aws/evidence/1126-outbound-rule-masked.png) | A: 전체 트래픽 허용 규칙, 어느 SG인지 미확인 |
| [등록 실패](../../aws/evidence/1126-domain-registration-failed-masked.png) | A: 도메인 등록 실패, Support 안내 |
| [도메인 불가](../../aws/evidence/1126-domain-unavailable-masked.png) | A: Given domain is unavailable. 원인 단정 불가 |

[NAT 실제 CLI](../../aws/verification/1126-aws-cli-masked.log): 1개 available. EKS 지원 버전 조회는 실제 생성된 클러스터 조회와 구분. [EKS 관찰 요약](../../aws/verification/1126-eks-observations.log): apply 후 1.37/ACTIVE, 워커 2 Ready, 시스템 Pod 6 Running, restart 0. 기존 AWS1 부분 verification의 내용은 이 파일에 보존하며, 전체 실행 점수로 계산되지 않게 evidence.json에서 implementation으로 분리한다.

## 11/27 캡처 전수 (9장)

| 공개 캡처 | 관찰 | 제한 |
| --- | --- | --- |
| [Blue TG](../../aws/evidence/1127-alb-blue-targets-masked.png) | A: IP/HTTP8080, 2 Healthy, 0 unhealthy | 이름은 마스킹, 파일·일지로 구분 |
| [Green TG](../../aws/evidence/1127-alb-green-targets-masked.png) | A: IP/HTTP8080, 2 Healthy, 0 unhealthy | 업무 앱 통합과 별도 |
| [HTTP 응답](../../aws/evidence/1127-alb-http-response-masked.png) | A: CI/CD Test test-v2 표시 | 상태코드 및 URL은 화면만으로 확정 불가 |
| [HTTP 리스너](../../aws/evidence/1127-alb-http-listener-masked.png) | A: HTTP80, 전달 가중치 100/0, stickiness off | HTTPS 아님 |
| [DB subnet group](../../aws/evidence/1127-rds-subnet-group-masked.png) | A: 2a/c 2개 서브넷 | EKS 노드 AZ와 별도 |
| [EFS AP](../../aws/evidence/1127-efs-access-point-masked.png) | A: AP 1개 Available, UID/GID 1500 | 실제 mount 및 해시 미증명 |
| [RDS](../../aws/evidence/1127-rds-instance-masked.png) | A: MariaDB db.t3.micro Available, AZ 2c, 3306, public access no | Multi-AZ DB 또는 데이터 복원 완료의 증거 아님 |
| [S3 버킷](../../aws/evidence/1127-s3-bucket-masked.png) | A: 서울 버킷, 생성 16:29:43 KST | 보안 설정 적용은 별도 |
| [S3 객체](../../aws/evidence/1127-s3-object-masked.png) | A: JPG 1개, 185.1 KB, 수정 16:33:23 KST | 이름 가림, 재다운로드 해시 별도 |

## AWS 상세 26항목

| 범위 | 결과 | 상태 |
| --- | --- | --- |
| VPC | 2AZ | A 구현 |
| Subnet | 6 Available | A 구현 |
| Route table | 4 | A 구현 |
| IGW | VPC 연결 | A 구현 |
| NAT | 1 available | A 구현 |
| SG | 서비스별 목록, SSH 규칙 | A 구현, 최소권한 전수 검사 미완 |
| EKS API | private true/public false, DescribeCluster ACTIVE | B 실행 |
| EKS worker | 2 Ready, 시스템 Pod 6 Running | B 실행 |
| EKS AZ | 서로 다른 두 노드에 각 슬롯 분산, 실제 AZ 라벨 미확보 | B 부분 |
| IAM/RBAC | notice 접근 및 port-forward 수정 후 성공, Node list 제한 | B 실행 |
| ECR | 태그/digest 실제 조회 및 CI push 대조 | A/B 실행 |
| ALB listener | HTTP80, 100/0 | A 구현 |
| ALB targets | Blue/Green 각각 Healthy 2 | A 실행 |
| ALB release | 정적 시험 전환/복귀, 연속 요청 | A/B 실행, 실앱 미검증 |
| RDS | private MariaDB Available | A 구현 |
| RDS migration | 14/1/6 및 digest 일치 담당자 보고 | C, 대상 원문 필요 |
| EFS AP | UID/GID 1500 | A 구현 |
| PVC | BOUND RWX 확인 기록 | B 실행 |
| EFS shared data | 두 AZ 테스트 Pod 파일 해시 일치 보고 | C, 대상 원문 필요 |
| S3 object | 1개 업로드, 표시 크기 원본과 부합 | A/B 구현 |
| S3 security/integrity | AES256, PAB, Versioning, 403, 해시 일치 보고 | C, 적용 후 원문 필요 |
| Route53/ACM | 등록 실패·HTTPS 보류 | D |
| CloudFront/OAC | 실제 첨부 다운로드 연계 미확인 | D |
| Redis | SG 이름 외 캐시 연결/fallback 미확인 | D |
| ASG | 워커 중단/대체 시간·서비스 영향 미측정 | D |
| CloudWatch | AWS 장애 관찰/운영 알림 수신 미확인 | D |

## 교차 검증: CI/CD, 서버, 인계

- [오전 검증](../../cicd/verification/1127-day2-midpoint.md): Private EKS 접근, notice RBAC, Blue/Green 2/2씩 Ready, 4 Pod Running, 포트포워드 HTTP 200. 다른 노드 배치와 다른 AZ 배치는 다르다.
- [ECR CLI](../../aws/verification/1127-ecr-images-masked.log): CI #3의 태그/digest와 일치. Jenkins CI 자체는 CI/CD 담당 성과.
- [CD #4](../../cicd/verification/1127-notice-cd-build-4-deploy.log): 정적 Green v3→v4, Blue v2 보존, 50초, ALB 변경 없음.
- [Release #4](../../cicd/verification/1127-notice-release-build-4-rollback.log): switch 22.98s, rollback 21.64s. [#5](../../cicd/verification/1127-notice-release-build-5-rollback.log): switch 20.23s, rollback 21.56s. [연속 조회](../../cicd/verification/1127-alb-continuity-summary.md): 341/341 HTTP PASS, 0 fail, Blue 301/Green 40. 정적 앱/합성 assertion 실패, CSV 원본 미등록. 절대 무중단·업무 RTO·워커 장애 복구와 구분.
- [CI→Plan](../../cicd/verification/1127-notice-plan-build-3-upstream.log): upstream 자동 호출, 13 tests, read-only. [Plan #5](../../cicd/verification/1127-notice-plan-build-5-functional.log): H2 격리 CRUD·숨김·삭제 확인, 19 tests; 실제 DB/EFS 아님.
- [최종 JSP 호환](../../cicd/verification/1127-pr21-final-compatibility.log), [UID/GID 1500](../../cicd/verification/1127-production-image-1500.log), [오후](../../cicd/verification/1127-day2-afternoon.log): CI #8 JUnit 8/8 및 ECR, Plan 20 tests, PVC Bound RWX, 17:24 Green patch applied. 최종 rollout/target health 미관찰, ALB 변경 없음. #25 draft는 아직 main 미병합.
- **이관 기준 시점 차이 발견:** 서버 [기준 캡처](../../server/evidence/2026-11-27/1127-13-migration-baseline-masked.png)와 [임시 복구 캡처](../../server/evidence/2026-11-27/1127-17-restore-test-masked.png)를 직접 읽으면 게시글/첨부/문의 14/1/2, 백업 임시 DB에서 동일하다. [14:04 인계 원문 발췌](../../aws/verification/1127-handoff-source-baseline-masked.log)는 14/1/6, 첨부 189,525 bytes 및 원본 해시 일치. 두 시점이 다르므로 2를 6으로 고쳐 쓰거나 임시 DB 복구를 RDS 복원으로 간주하지 않는다. [원본 첨부 화면](../../server/evidence/2026-11-27/1127-12-board-attach-sha256-masked.png)도 185.1KB 확인. S3와 이름·크기 대조는 보고되어 있으나 대상 해시 원문은 없음.
- [서버 검증표](../../server/verification/1127-ops-check.md): SSH·중앙 로그·백업·운영 메일·Prometheus 3/3. 본 AWS 감사에서 서버 30장 전체를 새로 판독하지 않았고 교차 검증 3장만 직접 열었다. CI/CD [증빙 인덱스](../../cicd/evidence/2026-11-27/README.md)는 PNG 38장 업로드 대기라고 명시한다. 네트워크 #26은 신규 실측 없는 인계 기록.
- [기존 AWS 이관 기록](../../aws/migration/1127-source-and-target-evidence.md)은 RDS/EFS/S3 대상 성공을 회수 요약으로 보존한다. 이번 대조에서 이를 독립적인 대상 원문으로 격상하지 않았다.

## 이정표별 판정과 남은 구체적 증거

| ID | 점수 | 구현 인정 사유 | 2점/추가 점수 조건 |
| --- | --- | --- | --- |
| AWS1 | 1/2 | 2AZ VPC 기반, 실제 EKS API·노드·Pod 사용 | 실제 EKS 연결 subnet/AZ, 권한 있는 주체의 노드별 zone 조회 |
| AWS2 | 1/2 | 실제 ALB 가중치·TG·정적 전환 및 복귀 | HTTPS/ACM, 실제 업무 앱 전환·복귀 및 검증 |
| AWS3 | 1/2 | RDS/EFS/S3 대상 구성, 객체 및 원본 기준 | 실제 이관 명령, RDS 대상 14/1/6과 digest, EFS/S3 대상 SHA256, 외부 직접 접근 차단 |
| AWS4 | 0/2 | 노드 그룹 기반만 있고 장애 관찰 핵심 구현 근거 부족 | ASG·CloudWatch 구성 및 워커 교체/장애 시 요청 영향·알림 실측 |

검증 원문을 보완할 때는 비밀값 및 관리 주소를 가리고 실행 시점·주체·대상·명령·관찰 결과를 남긴다. 이관 기준값은 실제 전환 직전에 다시 확정한다. 기존 0점 평가의 [원문](../../aws/operations/1128-progress-review.md)은 당시 정책으로 보존한다. 이 문서에서는 다른 팀원 성과를 AWS 단독 구현으로 중복 귀속하지 않았다.
