# 런북: 운영 알림이 오지 않음

- **시작 조건**: 시험 알람(`set-alarm-state`)·시험 배포 후 1분이 지나도 ops@에 메일 없음
- **영향**: 장애를 늦게 알게 된다
- **필요한 것**: 메일 서버(`10.0.30.10`) SSH(관리망 경유), AWS 콘솔 SQS 읽기 권한
- **상태**: 초안 · 미검증 · 설계 근거 [ADR-0002](../decisions/0002-alerts-sns-sqs-pull.md)

## 1. 상황 확인 (들어온 쪽에서 나간 쪽 순서로)

1. 메일 서버에 메일이 들어왔나: `maillog`에서 `status=sent` 확인.
2. AWS 알림이면 SQS에 메시지가 쌓여 있나(콘솔 “사용 가능한 메시지”).
3. 쌓여 있으면 메일 서버의 가져오기가 문제, 비어 있으면 SNS 구독·알람 쪽 문제.

```bash
sudo tail -n 50 /var/log/maillog
crontab -l | grep sqs2mail
sudo /opt/ops/sqs2mail.sh
curl -sS -o /dev/null -w '%{http_code}\n' https://sqs.ap-northeast-2.amazonaws.com
```

## 2. 조치

| 증상 | 조치 |
| --- | --- |
| SQS에 쌓여 있음 | 스크립트 수동 실행 결과 확인 → IAM 권한(Receive·Delete) → ASA 아웃바운드 443 |
| SQS 비어 있음 | SNS 주제의 SQS 구독·큐 정책 → 알람의 작업(SNS 주제) 확인 |
| Snort·백업 알림만 안 옴 | 보내는 서버의 `relayhost`, 메일 서버 `mynetworks`, SW ACL 25번 |

## 3. 끝났는지 확인

- [ ] 시험 알림이 1분 안에 ops@ 도착
- [ ] SQS 남은 메시지 0

## 4. 기록

- 원인과 고친 설정, [메일 수신 기록](../templates/server/mail-receipt-log.md)
