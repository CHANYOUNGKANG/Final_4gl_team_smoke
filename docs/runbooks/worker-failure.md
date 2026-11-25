# 런북: 워커 노드 장애

- **시작 조건**: `[장애] smoke-worker-down` (ALB HealthyHostCount < 2)
- **영향**: 정상이면 없음 — 다른 AZ 워커가 요청을 받는다
- **필요한 것**: AWS 콘솔 읽기 권한, `kubectl` 읽기 권한
- **상태**: 초안 · 미검증

## 1. 상황 확인

1. ALB 대상 그룹에서 unhealthy 대상과 AZ를 확인한다.
2. 운영 주소를 연속 조회해 사용자 영향(실패 요청)이 있는지 본다.

```bash
kubectl get nodes -o wide
kubectl -n "$K8S_NAMESPACE" get pods -o wide
aws autoscaling describe-scaling-activities --auto-scaling-group-name "$EKS_ASG" --max-items 5
```

## 2. 조치

1. ASG가 대체 워커를 띄우는지 지켜본다(손대지 않는 것이 기본).
2. 10분 넘게 대체 워커가 Ready가 아니면 노드 그룹 이벤트와 서브넷 IP 여유를 확인하고 이우빈에게 알린다.

## 3. 끝났는지 확인

- [ ] 대체 워커 `Ready`, 대상 그룹 healthy 2개 이상
- [ ] 복구 알림 메일 수신, 공지 조회 정상

## 4. 기록

- 중지 시각 → 첫 실패 → 회복 → 대체 워커 Ready 시각
- [장애 측정 양식](../templates/aws/failover-measure.md)과 결과 기록표 “워커 장애”
