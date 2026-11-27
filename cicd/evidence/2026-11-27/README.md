# CI/CD DAY 2 — 공개용 증빙 인덱스 (2026-11-27 KST)

## 수집 및 등록 상태

이 대화에 첨부된 실제 캡처 38장을 재사용해 공개용 사본을 준비했다. 01~22는 기존 마스킹 사본, 23~38은 원본에서 IP/ARN/관리 주소 등이 표시되는 영역을 마스킹하거나 잘라낸 사본이다. 재현 이미지나 가상 콘솔은 포함하지 않는다.

**PNG 파일 등록은 아직 대기 상태다.** GitHub의 저장소에는 인덱스만 등록되었으며, 로컬 바이너리 파일을 별도로 업로드한 후 실제 파일 수 및 내용 확인이 필요하다. 아래 파일명은 업로드 예정 이름이다.

| 파일명 | 내용 |
|---|---|
| `01-jenkins-dashboard.png` | Jenkins 기존 CI 성공 상태 |
| `02-ansible-gateway.png` | Ansible SSH 접속 |
| `03-jenkins-baseline.png` | Jenkins 서버 자원 및 버전 |
| `04-java17-install.png` | Java 17 빌드 환경 |
| `05-notice-ci-job.png` | 공지 앱 CI Job 생성 |
| `06-eks-describe.png` | EKS Private Endpoint 조회 |
| `07-kubectl-kubeconfig.png` | kubectl 및 kubeconfig 구성 |
| `08-rbac-initial.png` | namespace RBAC 확인 |
| `09-wrong-host.png` | 잘못된 서버에서 명령 실행한 문제 |
| `10-ecr-digests.png` | ECR 이미지 digest 조회 |
| `11-bootstrap-config.png` | EKS bootstrap 설정 |
| `12-dry-run.png` | Ansible dry-run |
| `13-node-rbac.png` | 클러스터 범위 노드 조회 제한 |
| `14-bootstrap-create.png` | bootstrap 최초 생성 |
| `15-bootstrap-success.png` | Deployment 생성 성공 |
| `16-pod-placement.png` | Blue/Green Pod 배치 |
| `17-portforward-failed.png` | Port-forward 실패 재현 |
| `18-portforward-error.png` | RBAC 오류 확인 |
| `19-subresource-no.png` | 하위 리소스 권한 부족 |
| `20-subresource-fixed.png` | 권한 수정 후 재검사 |
| `21-http-success.png` | Blue/Green HTTP 200 |
| `22-jenkins-remote.png` | Jenkins에서 Ansible 원격 조회 |
| `23-ci-scm-build-5-masked.png` | SCM 변경 감지 CI 성공 |
| `24-ci-main-scm-settings-masked.png` | main CI 브랜치 설정 |
| `25-cd-job-created-masked.png` | CD Job 생성 |
| `26-jenkins-remote-ecr-candidate-masked.png` | Jenkins 원격 EKS 조회 및 후보 digest |
| `27-stale-portforward-detected-masked.png` | 잔류 포트포워드 확인 |
| `28-stale-portforward-cleaned-masked.png` | 잔류 프로세스 제거 |
| `29-alb-initial-weights-masked.png` | HTTP 리스너 초기 가중치 100/0 |
| `30-alb-target-draining-masked.png` | 후보 업데이트 후 draining 확인 |
| `31-target-health-pod-match-masked.png` | Pod와 대상 그룹 상태 대조 (draining 진행 중) |
| `32-release-job-error-history-masked.png` | Release Job 최초 검증 및 실패 이력 |
| `33-continuity-start-masked.png` | 연속 HTTP 요청 시작 |
| `34-continuity-blue-green-transition-masked.png` | test-v2에서 test-v4로 전환 |
| `35-continuity-final-masked.png` | 341건 성공 / 실패 0건 최종 결과 |
| `36-ssh-session-settings-masked.png` | SSH 재접속 설정 화면 |
| `37-ansible-afternoon-health-masked.png` | 오후 EKS 상태, 권한 및 잔류 프로세스 확인 |
| `38-jenkins-afternoon-health-masked.png` | 오후 Jenkins/Docker 상태 및 테스트 컨테이너 제거 확인 |

## 관련 실행 로그 (이미 GitHub에 기록)

- [기본 CI 및 오전 검증](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/tree/main/cicd/verification)
- [PR #18: CD/Ansible](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/18)
- [PR #19: ALB 전환·롤백·연속 HTTP 검증](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/19)
- [PR #20: 실제 앱 CI→Plan 및 격리 H2 기능 검증](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/20)

정적 테스트 앱의 연속 HTTP 시험은 341건 중 341건 성공, 실패 0건으로 보고되었다. 이는 해당 샘플링 구간에 한정된 결과이며 실제 업무 앱의 RDS/EFS 및 무중단 검증은 별도다. 연속 요청 원본 CSV는 아직 미등록 상태다. 37~38번 캡처는 Jenkins/Docker active, EKS Deployment 2/2씩, Pod 4개 Running, Restart 0, 필요한 조회/patch/port-forward 권한 확인, 잔류 포트포워드 및 이전 기능 시험 컨테이너 없음의 근거다.

공개 저장소에 원본 스크린샷 또는 인증정보를 넣지 않는다. 실제 배포 관련 코드는 이 증빙 브랜치에서 변경하지 않는다.
