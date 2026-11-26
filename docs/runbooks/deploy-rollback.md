# 런북: 배포 실패 · 자동 롤백 확인

- **시작 조건**: 운영 메일함에 `[배포] 실패 · 롤백` 또는 Jenkins 빌드 실패
- **영향**: 전환 전 실패면 없음(Blue 유지). 전환 후 실패면 복귀까지 일부 요청 오류
- **필요한 것**: Jenkins 화면(실습 PC에서), Ansible EC2(`DEPLOY_HOST`), `kubectl` 읽기 권한
- **상태**: 초안 · 미검증 · 설계 근거 [ADR-0003](../decisions/0003-blue-green-single-eks.md)

## 1. 상황 확인

1. Jenkins 빌드 콘솔에서 **실패한 단계**를 본다: Test + WAR / Image → ECR / Green 배포 / Green 검사 / ALB 전환·관찰.
2. Green 검사 이전에서 멈췄다면 운영 트래픽은 Blue 그대로다 → 2-A.
3. ALB 전환 이후에 실패했다면 자동 복귀가 실행됐는지 콘솔 마지막 부분에서 확인한다 → 2-B.

## 2. 조치

**2-A 전환 전 실패**
1. 실패 로그를 `cicd/verification/build-<번호>.log`로 저장(주소 가림).
2. 원인을 고친 커밋을 push → 다음 빌드에서 Green 검사 통과 확인.

**2-B 전환 후 실패**
1. 운영 주소가 Blue 버전을 응답하는지 확인한다.
2. 응답하지 않으면 수동 복귀: `aws/operations/switch-to.sh blue` (이우빈 스크립트).
3. Green Deployment는 지우지 않고 원인 분석용으로 둔다.

```bash
kubectl -n "$K8S_NAMESPACE" get deploy,pods -l app=notice -o wide
kubectl -n "$K8S_NAMESPACE" logs deploy/notice-green --tail=100
curl -s -o /dev/null -w '%{http_code}\n' "$NOTICE_URL"
```

## 3. 끝났는지 확인

- [ ] 운영 주소 응답 200, 응답 버전 = 이전(Blue) 버전
- [ ] 연속 조회 로그에서 실패 요청 수와 복귀 시각 확인
- [ ] `[배포]` 결과 메일 수신

## 4. 기록

- 전환 시각 → 실패 판정 → 복귀 완료 시각, 실패 요청 수
- [결과 기록표](../delivery/README.md#결과-기록표) “전환 후 자동 롤백”에 반영
