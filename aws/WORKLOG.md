# AWS 작업일지 · 이우빈

최신 작업을 위에 누적한다. 담당자가 전달한 보고와 직접 실행 증빙을 구분한다.

## 2026-11-26 · Terraform EKS 및 Managed Node Group 구축

**담당자 보고** — Terraform으로 EKS와 Managed Node Group 구축 완료. 서울 리전, Kubernetes 1.37, 워커 v1.37.1-eks-9adbfea (버전은 보고값), t3.medium 2대, Amazon Linux 2023 x86_64, 두 프라이빗 앱 서브넷, Private Only API. 워커 2/2 Ready, 시스템 Pod 6/6 Running, Restart 0회로 보고됨.

**현재 진행 중** — Ansible 전용 IAM Role의 EKS Access Entry 및 notice namespace / smoke-deployers RBAC 설정. 완료 후 CI/CD 담당자에게 접속·권한 검증 요청 예정.

**후속 작업** — AWS Load Balancer Controller, ALB Blue/Green 대상 그룹 구성. 실제 앱 배포, RDS/EFS 인계, 트래픽 전환과 복구 검증은 별도.

**증빙** — [담당자 보고 및 인계 현황](infrastructure/eks-handoff-2026-11-26.md). Terraform 원본 및 실제 화면·로그 추가 제출 필요. 민감값은 제외했으며 공식 진행률 등록은 원본 근거 확보 후 진행.
