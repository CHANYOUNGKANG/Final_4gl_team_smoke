# 운영 메일 수신 기록

| 알림 | 발생 시각 | 수신 시각 | 제목 | 보낸 곳 | 결과 |
| --- | --- | --- | --- | --- | --- |
| [Snort] 탐지 |  |  |  | Snort → swatchdog |  |
| [백업] 결과 |  |  |  | cron 백업 |  |
| [장애] CloudWatch |  |  |  | SNS → SQS → sqs2mail |  |
| [Jenkins] 배포 |  |  |  | Jenkins → SNS → SQS |  |

`/var/log/maillog`의 해당 줄(status=sent)을 같은 폴더에 함께 저장한다.
