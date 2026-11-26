# Blue/Green 초기 테스트 배포 (작성본 · EKS 실행 전)

실제 공지 앱이 아닌 기존 smoke-test WAR 이미지 두 개를 사용한다. 운영 트래픽은 변경하지 않는다. `notice` 네임스페이스는 AWS 담당/관리자가 사전 생성한다.

| 항목 | Blue | Green |
| --- | --- | --- |
| Deployment | notice-blue | notice-green |
| Service | notice-blue-svc | notice-green-svc |
| Replica (제안값) | 2 | 2 |
| 초기 테스트 버전 | test-v2 | test-v3 |
| Pod/Service port | 8080 | 8080 |

Pod당 CPU request/limit 250m/500m, 메모리 512Mi/1Gi, JVM Xms128m/Xmx512m은 초기 제안값이지 실측이 아니다. 두 슬롯 총 4 Pod, requests 1 vCPU/2GiB. 노드 및 시스템 오버헤드 별도. readiness/startup/liveness는 실제 테스트 앱의 HTTP /를 사용한다. /health는 구현하지 않았다. 호스트별 분산은 best-effort이며 장애 시 가용성을 보장하지 않는다.

## 인계 후 실행 순서 (Ansible EC2, ansadmin)

1. 실제 EKS 클러스터명·버전·Access Entry·RBAC·노드 준비 확인. EKS 버전에 맞는 kubectl 설치. ECR Pull 권한 및 네트워크 확인.
2. 저장소의 검토된 커밋을 별도 작업 경로에 checkout. AWS CLI로 kubeconfig 구성 (기본 context는 클러스터 ARN, alias 사용하지 않음).
3. `cicd/config/bootstrap-smoke.vars.example.yml`을 저장소 밖으로 복사한 뒤 실제 context/ECR URI를 비공개로 입력. 기존 확인된 digest는 초기 테스트에만 사용. ECR에 해당 digest가 있는지 확인.
4. 저장소 루트에서 다음 명령으로 서버 dry-run. Namespace 및 RBAC 필요. 아래 파일은 로컬에 만든 비공개 변수 파일이다.

```bash
ansible-playbook -i localhost, -c local cicd/ansible/bootstrap-smoke.yml -e @/opt/devops/bootstrap-smoke.local.yml
```

5. AWS 담당과 용량·네임스페이스 확인, 기존 notice-blue/green 리소스가 없고 ALB 운영 트래픽이 연결되지 않았음을 확인한 뒤 명시적으로 생성.

```bash
ansible-playbook -i localhost, -c local cicd/ansible/bootstrap-smoke.yml -e @/opt/devops/bootstrap-smoke.local.yml -e '{"confirm_bootstrap":true}'
kubectl -n notice get deployment,service,pod -o wide
```

이 플레이북은 create-only이며 기존 Deployment/Service를 덮어쓰지 않는다. 중간 실패 시 일부 리소스가 남을 수 있으므로 다시 실행하기 전에 직접 상태를 확인한다. 오류 원인은 로컬에서 민감값을 가려 조사한다.

6. 각 서비스의 실제 버전 검사: 별도 Ansible EC2 터미널에서 `kubectl -n notice port-forward svc/notice-blue-svc 18080:8080`, 다른 터미널에서 `curl -fsS http://127.0.0.1:18080/`. Green도 포트 18081로 별도 실행하고 test-v3 확인. 이 검사는 초기 버전 확인용이며 ALB 검증과 별개다. port-forward 권한(pods/portforward)이 필요할 수 있다.

## 이후 구현

ALB 제어 방식 합의 후 TargetGroupBinding 또는 Ingress, 운영/후보 라우팅, 대상 그룹 healthy, 후보 버전 및 기능 확인, 자동 전환/복귀, 연속 요청 측정을 구현한다. 기존 운영 슬롯을 변경하기 전에 실제 트래픽 상태를 확인해야 한다. 이 초기 플레이북은 현재 Poll SCM 파이프라인에 연결하지 않는다. 실제 공지 앱 통합 및 외부 의존성은 별도다.
