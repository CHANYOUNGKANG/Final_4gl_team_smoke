# 2026-11-27 DAY 2 — EKS 접근 인계와 ALB Controller 설치

담당: 이우빈 · AWS. 11/26에 만든 EKS 기반을 11/27에 확인하고 CI/CD 담당자에게 넘긴 과정이다. 11/28에 회수한 자료를 **원래 작업일인 11/27**에 보완했다. 이번 문서화 중 AWS에 명령을 다시 실행하지 않았다.

[사용자 실행 결과 발췌](../verification/1127-recovered-user-results.log) · [11/26 기반 기록](eks-handoff-2026-11-26.md) · [실제 콘솔 캡처](1127-console-configuration.md) · [작업일지](../WORKLOG.md)

## 목적과 선택 이유

EKS는 앱 Pod의 실행 기반이고, 두 AZ의 워커는 한 영역에만 배치되는 구성을 피하기 위한 기반이다. 이 문서는 실제 배치·상태를 확인한 범위를 기록하며 장애 복구 시간이나 가용성 실측까지 완료로 확대하지 않는다. EKS Access Entry와 namespace RBAC는 Ansible 역할에 필요한 배포 권한을 전달하는 데 사용했다. AWS Load Balancer Controller는 Kubernetes와 ALB 대상 연결을 위한 구성 요소다. 기술의 목적과 실제 시험 결과는 아래에서 구분한다.

## 환경과 확인된 버전

| 항목 | 확인 내용 | 근거·범위 |
| --- | --- | --- |
| 리전·AZ | ap-northeast-2, ap-northeast-2a·2c | 09:17:41 사용자 노드 AZ 조회 |
| AWS 담당 실행 위치 | Terraform EC2 / ec2-user | 원래 사용자 메시지의 실행 문맥. 주소·계정 식별자는 제거 |
| EKS 제어 영역 | 1.37, ACTIVE, private endpoint true / public false | [팀 오전 인계 검증](../../cicd/verification/1127-day2-midpoint.md)의 DescribeCluster |
| 워커 | 두 노드 Ready, 각각 2a·2c | 09:17:41 사용자 출력 회수. 노드 주소는 공개하지 않음 |
| 워커 OS·버전 이력 | Amazon Linux 2023, amd64, v1.37.1-eks-9adbfea | [11/26 관찰](../verification/1126-eks-observations.log). 11/27에 새로 버전 명령을 실행한 것으로 쓰지 않음 |
| Helm | v4.3.2, KubeClientVersion v1.37, /usr/local/bin/helm | 11:05:34 사용자 출력 |
| LBC Helm chart | 3.6.2 | 같은 시각 실제 install의 --version |
| LBC 실제 이미지/App version | 미확인 | chart 버전으로 대체하지 않음 |
| Ansible 실행 위치·도구 | Ansible EC2 ansadmin, UID/GID 1001; kubectl 1.37.3, Kustomize 5.8.1 | [팀 오전 검증](../../cicd/verification/1127-day2-midpoint.md). AWS 담당의 로컬 설치 실적과 구분 |

## 실제 순서와 명령

### 09:17:41 — 두 AZ의 실행 상태 확인

출처는 파이널 프로젝트 DAY2 대화 검색에서 회수한 해당 시각 **사용자 명령·결과 요약**이다. 조회 대상 제목은 「261127 2일차」였으며 개별 검색 결과의 제목 반환 여부는 검증 로그에 구분했다. 전체 터미널 원문은 확보하지 못했으므로 노드 이름·AGE 등을 채워 넣은 가짜 표를 만들지 않았다.

```text
kubectl get nodes -L topology.kubernetes.io/zone
```

두 노드는 모두 Ready이며 각각 ap-northeast-2a와 ap-northeast-2c에 있었다. 같은 메시지의 전체 namespace Pod 조회에서는 Pod 6개 Running, 재시작 0을 확인했다. 이 결과는 EKS 두 AZ 실행 근거이며, DB 서브넷 그룹의 두 AZ 화면과는 별개다.

### 09:17:41 → 09:18:59 — Access Entry와 RBAC 그룹 불일치 해소

처음 회수한 설정은 Access Entry의 Kubernetes group이 `smoke-deployment`, RoleBinding의 Group이 `smoke-deployers`였다. 연결 Access Policy 목록은 빈 배열이었다. 09:18:59 사용자 후속 출력에는 Group `smoke-deployers`, Type `STANDARD`가 나타나 두 그룹이 일치했다.

어시스턴트가 안내한 update-access-entry 명령만으로 실행을 확정하지 않았다. 여기서 확인한 것은 **사용자 후속 설정 출력**이다. 실제 IAM 정책·Role/RoleBinding 전체 YAML과 변경 명령 원문은 미확보다. 빈 Access Policy 목록을 권한 없음 전체로 해석하지 않고, namespace RBAC로 허용되는 실제 동작을 별도로 본다.

이 시점 Ansible 역할은 DescribeCluster 성공, ListClusters AccessDenied, kubectl 미설치 상태였다. 이후 [팀 오전 로그](../../cicd/verification/1127-day2-midpoint.md)는 kubectl 설치와 private API 접속, notice Deployment·Service·Pod/log 권한을 확인했다. kube-system 생성·Node list 제한은 별도로 유지됐다. 따라서 오전 초기의 kubectl 미설치 상태를 당일 최종 상태로 반복하지 않는다.

### 11:05:34 — Helm으로 AWS Load Balancer Controller 설치

아래는 회수한 **실제 사용자 명령**이다. 원래 순서·옵션을 유지했고 실제 cluster 이름만 `$EKS_CLUSTER`로 치환했다. 기존 `$VPC_ID` 변수는 그대로 보존했다. 비밀값·변수값은 포함하지 않으며 이 문서에서 실행한 명령이 아니다.

```bash
helm install aws-load-balancer-controller eks/aws-load-balancer-controller --namespace kube-system --version 3.6.2 --set clusterName="$EKS_CLUSTER" --set region=ap-northeast-2 --set vpcId="$VPC_ID" --set serviceAccount.create=true --set serviceAccount.name=aws-load-balancer-controller --set replicaCount=2 --wait --timeout 10m
```

사용자 출력의 `STATUS: deployed`, `REVISION: 1`을 확인했다. chart를 고정하고 namespace·리전·VPC·서비스 계정·replica 수를 명시한 명령이다. replicaCount 2는 설치에 넘긴 값이며, 잘린 11:06:51 검색 결과만으로 컨트롤러 Pod 두 개의 Ready 상태나 이미지 태그를 추가 확정하지 않는다. 설치 전의 Deployment NotFound·Helm 미설치 기록은 경과로 구분한다.

## CI/CD와 연결한 결과

- **AWS 담당 자료:** 위 접근 설정, 노드 배치, Controller 설치 결과와 [ALB 대상 그룹·HTTP 리스너 캡처](1127-console-configuration.md).
- **강찬영의 팀 실행 자료:** [Ansible 접근·정적 앱 검증](../../cicd/verification/1127-day2-midpoint.md), [Release #5 전환·복귀](../../cicd/verification/1127-notice-release-build-5-rollback.log), [341회 조회 집계](../../cicd/verification/1127-alb-continuity-summary.md). Jenkins·Ansible 파이프라인을 AWS 개인의 단독 구현으로 기록하지 않는다.
- **당일 후속 상태:** 팀 17:24 격리 Green 후보 패치와 사용자 17:27:40의 Blue/Green 각 2개 Pod Running·PVC Bound/RWX가 확인됐다. 최종 후보의 rollout 완료·target health·업무 앱 RDS/EFS 연동은 별도 검증이 필요하다.

## 공통 설계와 실제 상태의 차이

| 공통 설계·기준 | 실제 확인 | 후속 처리 |
| --- | --- | --- |
| HTTPS 443 ALB와 도메인·인증서 | HTTP 80 리스너, 정적 응답, Blue/Green 대상 Healthy | HTTPS 완료로 기록하지 않음. 도메인·ACM·TLS 시험 필요 |
| LBC chart와 이미지 버전 각각 기록 | chart 3.6.2만 확정 | 실제 Deployment 이미지 태그 추가 조회 필요 |
| 노드 SG → RDS/EFS 허용 | 실제 캡처의 소스 SG는 EKS cluster SG로 표시 | 워커에 연결된 SG와 같은 허용 경계인지 인계에서 대조. 문서 작업으로 SG를 바꾸지 않음 |
| 루트의 Java/Maven/Tomcat 기준안 | 팀 DAY2는 Java17 앱·Jenkins Java21·Maven3.8.7·Tomcat10.1 | [DAY2 회의록](../../docs/daily/1127-meeting.md) 기준의 실제 인계 상태를 기록하고 공용 기준 변경은 합의 |

## 남은 자료

실제 Terraform 전체 원본, IAM·Access Entry/RBAC 설정 파일, LBC 실제 이미지 태그는 아직 확보하지 못했다. 이미 확인한 노드 AZ·그룹 후속 결과를 다시 보내 달라고 하지 않는다. 추가 자료가 들어오면 원래 작업 날짜에 연결하고, 원문 없는 파일을 당시 실행 코드처럼 복원하지 않는다.
