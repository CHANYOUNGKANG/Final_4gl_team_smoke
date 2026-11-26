# CICD3·4 AWS 인계 및 블루그린 협의안

2026-11-26 · 상태: 제안/인계 대기. 실제 값은 팀 비공개 채널과 Jenkins 설정으로 전달. 계정 ID, 실제 관리 IP, 개인 키, 토큰을 이 문서에 기록하지 않는다.

## 현재 검증한 범위

테스트 앱 GitHub 변경 → Jenkins Poll SCM → Maven/JUnit → WAR → Docker/Tomcat HTTP 200 → ECR 자동 Push 및 Digest 대조 성공. [Build #5](../verification/smoke-test-build-5-ecr.log). 실제 앱 인계 및 CD 검증은 별도다.

## AWS 담당 → CI/CD 담당 인계 체크리스트

| 항목 | 제안/요청 |
| --- | --- |
| Ansible EC2 | smoke-ansible (제안명), t3.micro, Ubuntu 24.04 LTS x86_64, gp3 15GiB, 프라이빗 IP만 |
| 배치 | 기존 VPC 10.100.0.0/16, 프라이빗 앱 10.100.11.0/24 (설계 대역) |
| 접속 | Jenkins 경유 TCP 22; 전용 배포 SSH 키의 공개키만 등록 권장, 실제 접속 값은 비공개 전달 |
| 아웃바운드 | NAT Gateway 또는 필요한 VPC endpoint, 패키지 저장소 HTTPS/필요 시 HTTP, DNS, AWS API 접근 |
| EKS | 단일 클러스터, 2개 프라이빗 앱 서브넷(10.100.11.0/24, 10.100.12.0/24), x86_64 워커 및 양쪽 버전 동시 수용량, private API endpoint |
| IAM·RBAC | Ansible EC2 전용 역할, eks:DescribeCluster, EKS Access Entry + 배포 네임스페이스 제한 RBAC(Deployment, Service, Pod 조회·배포, 필요시 Ingress/Job 등), 노드 역할 ECR Pull |
| ALB | HTTPS 443, HTTP 80 리다이렉트, AWS Load Balancer Controller 설치·버전, IP 대상 그룹 2개, 앱 포트 8080, 후보 검증 경로(접근 제한), ACM |
| 전환 권한 | Controller가 관리하는 Ingress 가중치 변경을 우선 협의. AWS API 직접 변경 시 리스너 규칙 소유권/재조정 충돌을 먼저 해결하고 대상 리소스에만 권한 부여 |
| 전달 값 | Ansible 사설 IP/사용자/SSH 접속 방법, IAM 역할·권한, 클러스터명·K8s 버전·네임스페이스, 노드/ASG 정보, ALB·대상 그룹/리스너 식별자, 전환 및 후보 검사 방식 |
| 비용 | 가동 시간·예산, NAT/EKS/ALB 비용, Blue/Green 중복 용량 합의 |

## 보안 그룹 연동 (추가 규칙, EKS 기본 필수 규칙 유지)

| 출발 | 도착 | TCP 포트 |
| --- | --- | --- |
| 실습 PC 공인 IP/32 | Jenkins SG | 22, 8080(필요 시; SSH 터널 권장) |
| Jenkins SG | Ansible SG | 22 |
| Ansible SG | EKS API endpoint SG | 443 |
| Jenkins / Ansible | 패키지 저장소 및 AWS API | 443, 필요 시 80 |
| EKS 워커 | ECR/S3 등 필요한 AWS 서비스 | 443 |
| 인터넷 | ALB SG | 80, 443 |
| ALB SG | 실제 대상 워커/Pod SG | 8080 |
| 워커/Pod SG | RDS / Redis / EFS SG | 각각 3306 / 6379 / 2049 (해당 서비스 사용 시) |

인바운드·아웃바운드 양쪽 규칙 및 라우팅을 확인한다. 기본 DNS, EKS 컨트롤 플레인/노드/CNI 통신은 유지한다. AWS 계정 키를 Jenkins에 저장하지 않는다.

## 블루그린 개념과 제안 이름

Blue/Green은 두 EC2가 아니라 동일 EKS 클러스터의 독립된 Deployment/Service 환경이다. 운영 슬롯과 후보 슬롯의 역할은 전환 후 교대한다.

| 대상 | Blue | Green |
| --- | --- | --- |
| Deployment | notice-blue | notice-green |
| Service | notice-blue-svc | notice-green-svc |
| 대상 그룹(제안명) | smoke-blue-tg | smoke-green-tg |
| 복제본 | 2 권장(용량 합의) | 2 권장(용량 합의) |
| 최초 테스트 이미지 태그 | test-7683373495abb6cfab7cbb2df46339cb2d83bb01 (v2) | test-32233749f3ae7ebf9cbc03b1b4d58ca6bb17a4b1 (v3) |

테스트 시에도 태그로 Digest를 확인하고 실제 배포는 Digest 고정 권장. 100:0 → 후보 검사 → 0:100 전환 → 운영 경로 검사 → 실패 시 이전 가중치 복원. 후보 실패 시 전환하지 않는다. 기존 슬롯을 복귀 기간 동안 유지한다. ALB 가중치만으로 자동 장애복귀가 보장되지 않으므로 명시적 상태 판정/롤백을 구현한다. 공용 DB 변경은 양 버전 호환성을 별도 검증한다.

## 역할 분담 및 완료 기준

AWS 담당: VPC·SG·NAT·EC2·IAM·EKS·ALB 기반 및 Controller 준비. CI/CD 담당: Ansible·AWS CLI·kubectl 설치, SSH 연동, 매니페스트·플레이북·Jenkins 배포 파이프라인, 전환/롤백 검증. ALB 제어 방식·후보 URL·권한은 공동 합의.

1. Jenkins에서 Ansible 사설 SSH 접속 및 Ansible에서 EKS 접근 확인.
2. 기존/후보 이미지 동시 실행, readiness 및 후보 HTTP/버전 검증.
3. 후보 실패 시 운영 버전 유지 확인.
4. 정상 전환 후 운영 버전 확인, 실패 주입 후 자동 복귀.
5. 연속 요청 수/실패 수, 전환·복귀 시각, Git SHA·ECR Digest·Jenkins 번호 기록.
6. 실제 공지 앱 인계 후 게시글 작성·조회 및 데이터 호환 검증.

관련: [IP 설계](../../docs/architecture/ip-plan.md), [인계표](../../docs/delivery/README.md), [CI/CD](../README.md). 아직 구현·실행 전이며 제안값은 확정 설정이 아니다.
