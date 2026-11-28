# 메일 계정 (비밀번호는 서버에만)

| 계정 | 셸 | 용도 |
| --- | --- | --- |
| user1, user2 | 일반 | 송수신 시험 |
| smoke | `/sbin/nologin` | 운영 알림 메일함 `smoke@smoke.local` (문의·백업·장애·배포) |

```bash
sudo useradd -m -s /sbin/nologin smoke
sudo passwd smoke          # Roundcube 로그인용. 값은 저장소·캡처에 남기지 않는다
```
