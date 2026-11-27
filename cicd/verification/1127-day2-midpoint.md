# 2026-11-27 DAY 2 오전 중간 저장 (10:35 KST)

## 실제 업무 앱 CI — smoke-notice-ci
- Jenkins UI 및 기존 smoke-cicd #10 성공 상태 확인. Java 21.0.13.1 유지, Java 17.0.21.1 추가, Jenkins active. Maven 3.8.7, Docker 29.10.1, 디스크 조회 시 11GB 가용.
- 별도 Pipeline script from SCM, branch `*/cicd/notice-ci-integration`, script `cicd/jenkins/Jenkinsfile.notice-ci`. HTTPS 공개 저장소, Poll SCM H/2 * * * * 코드 선언. 기존 Job 보존.
- 실제 팀 표준 app/ Git SHA `77bd103e06c6609478a566a5513e22d6747e9d34`, Spring Boot 3.3.5, Java 17, notice.war. 세 빌드 모두 Started by user.
| Build | 로그 시간(KST) | Maven | 테스트 | 완료 |
|---|---|---|---|---|
| #1 | 09:43:30~09:44:22 (52초) | 43.225초 | 10/10 | WAR |
| #2 | 10:06:59~10:08:09 (70초) | 25.406초 | 10/10 | Docker H2 |
| #3 | 10:09:36~10:10:45 (69초) | 31.450초 | 10/10 | ECR Push VERIFIED |
- [Build #1 콘솔](1127-notice-ci-build-1.log), [Build #2 콘솔](1127-notice-ci-build-2.log), [Build #3 콘솔](1127-notice-ci-build-3.log). 붙여넣은 로그의 형식을 정규화하고 민감 식별자 마스킹.
- Build #3 WAR SHA-256 `42b04def772b468482ec84701b8d42d5e997fb7827f64c43da595f986ebaedd2`.
- ECR tag `notice-77bd103e06c6609478a566a5513e22d6747e9d34-3`, digest `sha256:08a1e4d2d695fa2923b3881233e08b22da6262eb190c54995c0630867845524d`. linux/amd64, non-root app, H2 격리 테스트 성공. ECR 인증 임시 디렉터리 사용 및 종료 시 삭제 코드를 확인.
- 아직 실제 앱의 Git 변경 자동 실행 및 자동 ECR Push 검증은 아님. 기본 NOTICE_DOCKER_CHECK / NOTICE_ECR_PUSH false. 실제 RDS/EFS 및 EKS 업무 앱 배포 미검증.

## Ansible → EKS 초기 정적 테스트 배포
아래는 사용자 제공 터미널 화면을 읽어 정리한 관찰 기록이며 별도 생성한 원본 콘솔 로그가 아니다.
- ansadmin UID/GID 1001, /opt/devops 0750. AWS STS assumed-role smoke-ansible-role, DescribeCluster 성공: smoke-eks 1.37 ACTIVE, private True public False. kubectl v1.37.3 / checksum OK, Kustomize v5.8.1, ansadmin kubeconfig 생성 및 API 조회 성공.
- notice Deployment 및 Service get/list/watch/create/patch/update yes, Pod get/list/watch 및 실제 logs get yes. kube-system Deployment create no. Node list Forbidden: cluster scope의 최소 권한 제한.
- ECR 테스트 이미지 존재 및 digest 일치: Blue `sha256:89cbb9d7197385f7a77bec308ef85826d86e54180a5c7ffb5aec0af76b290cea`, Green `sha256:c310410ef3f7449678920ea39699772c9a31be67fa06a9e0a46ab5a392123568`.
- 검토된 main `1930c3b12e7d092de190ffa0bd99474075df2342`를 /opt/devops/smoke-bootstrap-day2에 clone 및 checkout --detach. 저장소 외부 /opt/devops/bootstrap-smoke.local.yml 0600 (실제 값 미공개).
- syntax-check 성공, dry-run: ok=5 changed=0 unreachable=0 failed=0 skipped=3 rescued=0 ignored=0.
- confirm_bootstrap=true 실제 create-only 실행: ok=8 changed=1 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0. Blue/Green rollout 완료. ALB 변경 없음.
| 리소스 | 관찰 |
|---|---|
| notice-blue | 2/2 Ready, 2 available |
| notice-green | 2/2 Ready, 2 available |
| notice-blue-svc, notice-green-svc | ClusterIP, 8080/TCP |
| Pod | 4개 1/1 Running, restart 0 |
| 분산 | 서로 다른 두 워커에 각 색상 하나씩 배치; 노드 AZ 라벨 미확인 |
- Jenkins 서비스 계정 jenkins로 SSH (BatchMode, StrictHostKeyChecking, IdentitiesOnly) → ansadmin → hostname/whoami/kubectl 조회 성공. 실제 CD Job에서 업데이트한 것은 아님.

## 오류 해결
1. Ansible에서 jenkins 계정으로 ECR 조회: unknown user jenkins. Jenkins 서버로 이동 후 성공. WAR 경로를 실행한 Permission denied는 빌드 실패가 아님.
2. 초기 Port Forward: curl (7), 로그에 pods/portforward create Forbidden. 최초 `kubectl auth can-i create pods/portforward`는 하위 리소스를 정확히 검사하지 못했음.
3. `kubectl auth can-i get pods --subresource=portforward -n notice` / create 각각 no, `kubectl auth can-i get pods --subresource=log -n notice` yes. AWS 담당자에게 Role에 아래 규칙 요청.
```yaml
- apiGroups: [""]
  resources: ["pods/portforward"]
  verbs: ["get", "create"]
```
4. 권한 재검사 get/create 모두 yes; 별도 Pod 재배포 없이 localhost Port Forward 검증 성공.
```text
BLUE SERVICE: <p id="version">test-v2</p>
HTTP STATUS: 200
GREEN SERVICE: <p id="version">test-v3</p>
HTTP STATUS: 200
SERVICE CHECK COMPLETE
```
Port Forward는 Service를 지정해 선택된 Pod에 연결한 내부 검증이며 실제 ClusterIP 데이터 경로/ALB 검증과는 구분한다.

## 재현 및 다음 단계
- [초기 배포 가이드](../kubernetes/README.md), [플레이북](../ansible/bootstrap-smoke.yml), [변수 예시](../config/bootstrap-smoke.vars.example.yml), [실제 앱 CI](../jenkins/Jenkinsfile.notice-ci).
- Ansible: `kubectl -n notice get deployments,services,pods`, `kubectl auth can-i create pods --subresource=portforward -n notice`. 이미 생성한 create-only 플레이북 재실행 금지.
- 내부 검증: `kubectl -n notice port-forward --address 127.0.0.1 svc/notice-blue-svc 18080:8080` 후 별도 터미널 `curl -fsS http://127.0.0.1:18080/`; Green 18081. Forwarding from 준비 확인 및 종료.
- 실제 앱 SCM 자동 실행 증명, ECR 자동 등록 정책 결정, PR #13 검사 및 병합 후 main 감시 검증.
- 실제 앱 CD 후보 슬롯 갱신, RDS/EFS/Secret, ALB/TG, 전환·자동 복귀 및 연속 요청/복구 시간 검증.
- 공식 진행률 증빙 추가 및 판정은 완료 기준 충족 후. 이 중간 저장만으로 CICD3/4 완료 또는 전체 자동화 성공으로 표시하지 않는다.
- 실제 캡처 22장은 마스킹한 별도 PDF/ZIP으로 준비. 이 기록의 캡처는 아직 저장소에 바이너리 업로드되지 않음.
