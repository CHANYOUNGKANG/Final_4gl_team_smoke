# smoke-notice-cd · 초기 정적 후보 검증

Jenkins Pipeline script from SCM → Git → 공개 팀 저장소 → */cicd/notice-cd-integration → cicd/jenkins/Jenkinsfile.notice-cd. 트리거 없음. 기존 전역 SMOKE_ANSIBLE_HOST, SMOKE_AWS_REGION, SMOKE_ECR_REPO 및 전용 SSH 키/known_hosts 재사용. Ansible 서버의 기존 /opt/devops/bootstrap-smoke.local.yml 사용. 실제 값은 공개하지 않는다.

| 모드 | 동작 |
| --- | --- |
| VERIFY (기본) | 기존 Blue v2 / Green v3 이미지·rollout·2 Ready·서비스 지정 port-forward HTTP 200 및 버전 검증. 변경 없음 |
| PLAN | 검증 후 별도의 test-v4 이미지 tag를 ECR digest로 해석하고 Green JSON patch server dry-run |
| DEPLOY | AWS 담당자가 Green 트래픽 미연결과 용량을 확인한 경우에만 명시 체크 후 Green 이미지 변경, v4 검사 및 Blue v2 재확인 |

초기 검증은 Blue와 Green의 기존 digest를 정확히 검사한다. 실제 앱 notice-* 이미지는 허용하지 않는다. PLAN/DEPLOY에 사용할 후보 test-* 태그는 정적 앱 v4의 성공한 Jenkins 로그에서 확인한 것만 사용한다. Green 변경은 기존 이미지에 대한 JSON Patch test 조건을 포함한다. 서비스·ALB·Blue 배포는 변경하지 않는다. Port-forward는 선택된 Pod 응답 확인이며 ALB 또는 ClusterIP 데이터 경로 검증은 아니다. Green 변경 후 실패하면 Job을 실패로 표시하며 기존 운영 ALB를 변경하지 않는다. 자동 롤백은 아직 없다. 성공 후에도 재실행은 초기 Green v3 조건으로 차단된다. 재실행 전 실제 상태를 확인하고 후속 플레이북을 설계한다.

첫 실행은 VERIFY, CANDIDATE_TAG 공란, CONFIRM_GREEN_OFFLINE=false. 기대 로그: SLOT blue READY=2 HTTP=200 VERSION=test-v2, SLOT green READY=2 HTTP=200 VERSION=test-v3, CD VERIFY OK, NOTICE CD OK. 실패 시 기존 Pod 삭제/부트스트랩 재실행 금지.
