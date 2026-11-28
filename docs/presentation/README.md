# 발표 자료 후보

최종 발표(12/9)에 쓸 캡처·로그·도식을 모으는 색인이다. 캡처를 올릴 때 한 줄씩 추가하면 발표 준비 때 슬라이드 순서대로 옮기기만 하면 된다.

**규칙**　민감값을 가린 사본(`*-masked.png`)만 링크한다. 슬라이드 설명은 “무엇을 했다”가 아니라 **“이 화면이 무엇을 증명하는가”**로 쓴다.

## 슬라이드 흐름 (초안)

| # | 장 | 담는 내용 | 담당 |
| ---: | --- | --- | --- |
| 1 | 문제 정의 | 고객 시나리오 · 조건 3가지 | 이준호 |
| 2 | 전체 아키텍처 | 온프레미스 ↔ AWS ↔ CI/CD 구성도 | 전원 |
| 3 | 네트워크 분리·접근 통제 | 허용·차단 결과, 절체 시간, IDS 탐지 | 강민서 |
| 4 | 서버 정비·원본 보존 | 백업·해시 목록, 운영 메일 수신 | 이준호 |
| 5 | AWS 이관·가용성 | 이관 대조표, 워커 장애 복구 시간 | 이우빈 |
| 6 | 무중단 배포·자동 롤백 | 커밋 → Jenkins → ECR → Green → 전환, 실패 0건 · 롤백 시간 | 강찬영 |
| 7 | 운영 알림 통합 | 알림 4종 수신 화면 | 이준호 |
| 8 | 비용·회고 | 예상 vs 실제 비용, 남은 과제 | 이우빈 · 전원 |

## 증빙 색인

| 날짜 | 파트 | 파일 (가린 사본) | 이 화면이 증명하는 것 | 슬라이드 설명 문구 | 장 |
| --- | --- | --- | --- | --- | ---: |
| 11/26 | 서버 | [1126-11-ansible-common-playbook-masked.png](../../server/evidence/2026-11-26/1126-11-ansible-common-playbook-masked.png) | mgmt 한 곳에서 3대 서버 기본 설정을 코드로 일괄 적용(failed=0) | 서버 표준화 자동화 — 손으로 하던 설정을 플레이북 한 번으로 | 4 |
| 11/26 | 서버 | [1126-12-data-lvm-mount-masked.png](../../server/evidence/2026-11-26/1126-12-data-lvm-mount-masked.png) | 데이터 디스크를 LVM 으로 첨부(5G)·DB(4G)로 나누고 확장용 디스크를 남김 | 디스크 부족 문제를 볼륨 분리와 무중단 확장으로 대비 | 4 |
| 11/26 | 서버 | [1126-13-mariadb-smoke-board-masked.png](../../server/evidence/2026-11-26/1126-13-mariadb-smoke-board-masked.png) | 이관 기준 DB 가 분류별 8건으로 구성되고 대조 뷰가 본문 해시를 계산 | 이관 전후 비교 기준값 확보 | 4 |
| 11/26 | 서버 | [1126-19-notice-health-ok-masked.png](../../server/evidence/2026-11-26/1126-19-notice-health-ok-masked.png) | web 의 Tomcat 공지 앱이 data 의 MariaDB 를 읽어 8건 응답 | 온프레미스 3-Tier 동작 | 4 |
| 11/26 | 서버 | [1126-07-trouble-l2-loop-ping-dup-masked.png](../../server/evidence/2026-11-26/1126-07-trouble-l2-loop-ping-dup-masked.png) | GNS3 이중 연결로 생긴 L2 루프 증상(응답 중복·지연 증가) | 장애 원인 분석 사례 — 이중 경로 제거로 해결 | 4 |
| 11/26 | AWS | [VPC 리소스맵](../../aws/evidence/1126-vpc-map-masked.png) | 두 AZ의 public/app/data 서브넷 6개와 라우팅·IGW/NAT 항목 | 서비스 계층을 두 AZ에 나눈 기반 구성. EKS 노드의 실제 AZ 배치 검증은 별도 | 2 |
| 11/26 | AWS | [서브넷 상태](../../aws/evidence/1126-subnets-masked.png) | 서브넷 6개가 모두 Available | 네트워크 기반의 실제 콘솔 상태 확인 | 5 |
| 11/26 | AWS | [보안 그룹 목록](../../aws/evidence/1126-security-groups-masked.png) | 서비스별 SG가 존재함 | 서비스 목적별 SG 구성. 이름만으로 규칙 전체 적용을 입증하지 않음 | 3 |
| 11/26 | AWS | [Ansible 인바운드](../../aws/evidence/1126-ansible-ssh-rule-masked.png) | SSH/TCP 22의 출발지 SG 참조. 원본 SG 목록과 대조해 Jenkins SG임을 확인 | Jenkins에서 Ansible로 연결하는 허용 경계. SSH 성공은 팀원 로그로 별도 확인 | 6 |
| 11/26 | AWS | [아웃바운드 규칙](../../aws/evidence/1126-outbound-rule-masked.png) | 모든 트래픽·전체 포트·0.0.0.0/0 규칙 1개 | 실제 설정과 최소 권한 목표의 차이. 화면만으로 소속 SG는 확정할 수 없음 | 8 |
| 11/26 | AWS | [도메인 등록 실패](../../aws/evidence/1126-domain-registration-failed-masked.png) | 11/26 09:45 KST 제출 건의 실패와 AWS Support 안내 | 실패를 기록하고 초기 HTTP·추후 HTTPS 전환 기준과 연결 | 8 |
| 11/26 | AWS | [도메인 사용 불가](../../aws/evidence/1126-domain-unavailable-masked.png) | Given domain is unavailable 오류 | 성공 자료와 실패 자료를 분리해 원인 확인 범위를 기록 | 8 |
| 11/26 | AWS | [EKS 관찰 요약](../../aws/verification/1126-eks-observations.log) | 실제 대화 출력에서 노드 2대 Ready·시스템 Pod 6개 Running 회수 | Kubernetes 기반의 관찰 시점 상태. 원본 스크린샷·노드 AZ·업무 앱 배포 증거와 구분 | 5 |
| 11/26 | AWS | [CLI 원문 공개용 발췌](../../aws/verification/1126-aws-cli-masked.log) | EKS 1.37 지원 조회와 NAT Gateway 1개 available | 지원 버전 조회는 클러스터 배포 증거와 다름. NAT는 실제 사용자 제출 출력 | 5 |

### AWS 자료 사용 범위

11/26은 자료 정리·업로드 기준일이다. 화면에 시각이 보이는 도메인 등록 실패 자료 외의 원본은 정확한 캡처 시각과 리소스 생성 시각을 단정하지 않는다. 실제 스크린샷의 민감 부분만 불투명하게 제거하고 메타데이터를 지웠으며 성공 화면을 생성하지 않았다. 실패·보류·미검증 자료를 성과 지표로 바꾸지 않는다.

[AWS 상세 설명·출처](../../aws/WORKLOG.md) · [AWS 현황](../../aws/README.md)

## AWS · 11/27 실제 구축 화면 (11/28 회수)

담당: 이우빈. 각 자료의 출처·업로드 시각·증명 범위는 [AWS 작업일지](../../aws/WORKLOG.md)와 [구성 기록](../../aws/infrastructure/1127-console-configuration.md)에 있다. 실제 원본을 마스킹한 사본이며 생성 전 설정 양식은 성공 증빙에 포함하지 않았다.

| 발표 후보 | 실제 화면 | 설명과 한계 |
| --- | --- | --- |
| Blue/Green 대상 준비 | [Blue](../../aws/evidence/1127-alb-blue-targets-masked.png), [Green](../../aws/evidence/1127-alb-green-targets-masked.png) | 대상 그룹 각각 Healthy 2개. 팀원 파이프라인의 전환·복귀 로그와 함께 설명 |
| HTTP 경로와 리스너 | [test-v2 응답](../../aws/evidence/1127-alb-http-response-masked.png), [HTTP80 리스너](../../aws/evidence/1127-alb-http-listener-masked.png) | 실제 정적 시험 응답 및 Blue100/Green0. HTTPS 완료로 제시하지 않음 |
| DB 대상 준비 | [DB subnet group](../../aws/evidence/1127-rds-subnet-group-masked.png), [RDS](../../aws/evidence/1127-rds-instance-masked.png) | 두 AZ DB subnet group 및 RDS 사용 가능·private. EKS 두 AZ 배치 또는 DB 복원 무결성과 구분 |
| 공유 파일 저장소 | [EFS Access Point](../../aws/evidence/1127-efs-access-point-masked.png) | 사용 가능·UID/GID1500. 실제 마운트·해시 검증은 별도 |
| 이관 원본과 S3 대상 | [버킷](../../aws/evidence/1127-s3-bucket-masked.png), [객체](../../aws/evidence/1127-s3-object-masked.png) | S3 객체1개·표시크기와 원본 목록 대응. [원본 기준값](../../aws/verification/1127-handoff-source-baseline-masked.log)은 온프레미스이며 RDS 복원 후 결과가 아님 |
