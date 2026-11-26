# EKS 구축 및 CI/CD 인계 현황 · 2026-11-26

- 담당: 이우빈 (AWS)
- 출처: 팀원이 전달한 구축 결과 보고 (2026-11-26), 공개용 정리본
- 상태: EKS 및 Managed Node Group 구축 완료 보고, 배포 권한 설정 진행 중
- 증빙 범위: 담당자 보고 내용. Terraform 원본, AWS 조회 결과, kubectl 원본 로그 및 화면은 아직 제출되지 않아 독립 확인하지 않았다.

## 구축 환경 (담당자 보고 기준)

| 항목 | 내용 |
| --- | --- |
| 구축 방식 | Terraform |
| 클러스터 | 팀의 단일 EKS 클러스터 (실제 이름은 비공개 인계) |
| 리전 | ap-northeast-2 |
| Kubernetes | 1.37 (보고값, API 조회로 재확인 필요) |
| 워커 kubelet 버전 | v1.37.1-eks-9adbfea (보고값) |
| 노드 그룹 | Managed Node Group |
| 워커 | t3.medium 2대 |
| 노드 OS | Amazon Linux 2023 x86_64 |
| 배치 | 두 프라이빗 앱 서브넷, 워커 각 1대 (보고 기준) |
| API Endpoint | Private Only |
| Cluster SG | 실제 식별자는 비공개 인계 |

워커 실제 IP, SG ID, 계정 ID, ARN, kubeconfig 및 실제 접속 값은 공개하지 않는다.

## 보고된 검증 결과

| 검사 | 결과 |
| --- | --- |
| 워커 상태 | 2/2 Ready |
| 시스템 Pod | 6/6 Running |
| Pod Restart | 0회 |

위 수치는 담당자가 전달한 결과이며, 이번 문서 작성 과정에서 직접 실행한 결과가 아니다. 시스템 Pod 수 및 재시작 횟수는 관측 시점 기준이다.

## CI/CD 인계 조건

| 항목 | 상태 |
| --- | --- |
| Ansible EC2 IAM Role | 기존 전용 역할 사용 기준 |
| EKS Access Entry | 설정 진행 중 |
| 배포 Namespace | notice (배포 기준) |
| Kubernetes Group | smoke-deployers (권한 구성 기준) |
| Namespace RBAC | 설정 진행 중 |
| Ansible → private API endpoint 접속 | 검증 요청 전 |
| AWS Load Balancer Controller | 후속 구성 예정 |
| ALB Blue/Green 대상 그룹 | 후속 구성 예정 |

## 다음 검증

1. AWS 담당자가 실제 클러스터명, EKS API 버전, Access Entry, namespace 및 RBAC 설정을 비공개로 인계한다.
2. Ansible EC2에서 AWS CLI로 클러스터 버전/상태 및 private endpoint 설정을 확인하고, 확인된 서버 버전에 맞는 kubectl을 설치한다.
3. Ansible EC2의 배포 계정으로 Kubernetes 인증 및 notice namespace 내 Deployment/Service 조회·생성·변경 권한을 검사한다. 필요한 범위만 허용하고 cluster-admin을 기본 부여하지 않는다.
4. 기존 테스트 이미지의 ECR Pull, Blue/Green Pod readiness와 서비스별 응답을 확인한다.
5. AWS Load Balancer Controller, 대상 그룹 및 전환 방식 확정 후 후보 검사·전환·복귀를 검증한다.

실제 EKS 배포와 ALB 전환은 이번 기록의 완료 범위가 아니다. [CI/CD 인계 문서](../../cicd/ansible/HANDOFF.md), [초기 배포 가이드](../../cicd/kubernetes/README.md), [인계 이슈 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11).

## 추가 제출 자료

- Terraform 구성 파일(.tf), 변수 예시 및 민감값을 제외한 모듈 구조 (tfstate, 실제 tfvars, 자격 증명 제외)
- 마스킹한 EKS/Managed Node Group 구성 및 두 서브넷 배치 화면
- kubectl get nodes 및 시스템 Pod 상태의 실제 검증 로그/캡처
- Access Entry, Role/RoleBinding 및 Ansible에서의 인증·권한 검증 결과

실제 자료가 제공되면 기존 기록에 추가하고 AWS1 완료 기준에 맞춰 진행률 근거를 등록한다. 현재는 담당자 보고만 보존하며 점수 등록은 보류한다.
