# 사내 메일·운영 알림

[← 서버 파트](../README.md) · 확인 기록 [11/27 §7·§8](../verification/1127-ops-check.md#7-사내-메일-srv4)

## 구성 (web 서버)

```
브라우저 → Nginx /webmail/ → PHP-FPM → Roundcube 1.7.0 (설정 DB: data MariaDB roundcubemail)
                                         └ IMAP → Dovecot 2.3.21 → ~/Maildir
보내는 쪽(Tomcat·data 백업·mgmt) → Postfix 25 → 로컬 배달 → ~/Maildir
```

| 항목 | 값 | 이유 |
| --- | --- | --- |
| 도메인 | `smoke.local`, `myhostname = mail.smoke.local` | 사내 전용 |
| 발송 허용 | `mynetworks` = 루프백 · 사내 대역 · (임시) NAT 대역 | 외부 스팸 중계 차단 |
| 저장 | `home_mailbox = Maildir/`, 메시지 20MB 제한 | 메일 1통 = 파일 1개, 백업·복구 쉬움 |
| Dovecot | `auth_username_format = %Ln` | Roundcube 가 `user@smoke.local` 로 로그인해도 시스템 계정으로 인증 |
| Roundcube | `public_html` 만 웹에 노출, 회사 테마 플러그인 | 설정 파일·DB 정보 비공개 |
| 계정 | user1, user2, smoke(로그인 셸 없음) | smoke = 운영 알림 메일함 |

## 운영 알림 메일함 smoke@smoke.local

| 알림 | 경로 | 상태 |
| --- | --- | --- |
| 홈페이지 문의 | Tomcat `MAIL_TO` → Postfix | ✅ 수신 확인 |
| 백업 성공·실패 | data 래퍼 → `MAIL_RELAY_HOST:25` | ✅ 수신 확인 |
| 배포 결과·롤백 | Jenkins → SNS → SQS → mgmt 수신 스크립트 → Postfix | ⏳ AWS SQS 준비 후 |
| AWS 장애 | CloudWatch → SNS → SQS → (같은 경로) | ⏳ |
| 온프레미스 장애 | Grafana 알림 → Postfix | ⏳ 규칙 작성 전 |
| 공격 탐지 | Snort → swatchdog → Postfix | ⏳ 네트워크 연동 후 |

### AWS 알림을 SQS 로 받는 이유

온프레미스는 아직 VPN 없이 VMware NAT 로만 나간다. AWS 가 사내 메일 서버로 **들어오는** 연결은 불가능하고, SNS 이메일 구독은 `.local` 주소로 배달되지 않는다. mgmt 가 SQS 를 HTTPS 로 **꺼내 오는** 방식은 밖으로 나가는 연결이라 NAT 로도 된다.

- SQS 구독은 `RawMessageDelivery=false` → SNS 메시지의 `Subject`·`Message` 를 메일 제목·본문으로 사용 (CI/CD PR #23 과 합의)
- 온프레미스에는 EC2 역할이 없으므로 해당 대기열의 `ReceiveMessage`·`DeleteMessage`·`GetQueueAttributes` 만 허용한 전용 키를 mgmt root 전용 파일에만 둔다. 키·대기열 URL 은 저장소에 올리지 않는다 (`AWS_REGION`, `ALERT_QUEUE_URL`)
- VPN 연결 후에는 Jenkins 가 `MAIL_RELAY_HOST:25` 로 직접 보내는 방식도 가능 (web 방화벽·`mynetworks` 는 Jenkins 출발지 IP 하나만 허용)
