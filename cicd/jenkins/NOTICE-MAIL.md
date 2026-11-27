# 사내 메일 배포 알림 (11/27)

## 연동 조건
- Jenkins controller: AWS EC2, VPC 10.100.0.0/16, 설계상 public subnet A 10.100.1.0/24. 실제 IP와 SMTP 목적지, VPN/NAT 경로는 담당자와 비공개 확인한다.
- SMTP: MAIL_RELAY_HOST의 실제 값은 Jenkins System에만 설정. TCP 25, 인증 없음은 격리된 사내 경로에서만 허용. 메일 서버 firewall/Postfix에서 관측된 Jenkins 출발지 IP만 허용하고 수신자/발신자 제한. 인터넷 공개 릴레이 금지.
- EC2 TCP 25 제한 가능. 네트워크 담당자와 라우팅, SG egress, ASA/VPN ACL, 메일 서버 수신을 확인하고 필요시 승인된 내부 SMTP 대체 포트 협의.
- Manage Jenkins → Plugins에서 Mailer 확인, Manage Jenkins → System → E-mail Notification에 SMTP server, port 25, authentication off, SSL/TLS 설정은 서버와 합의. Jenkins Location의 System Admin e-mail address: jenkins@smoke.local. 실제 SMTP 서버 주소/접속 정보 GitHub에 저장 금지.

## 독립 테스트 (운영 변경 없음)
Job: smoke-notice-mail-test, Pipeline script from SCM, repository team repo, branch = 이 PR의 검토 브랜치(병합 이후 main), Script Path cicd/jenkins/Jenkinsfile.notice-mail-test. Poll SCM 없음. Build with Parameters에서 CONFIRM_MAIL_TEST=true로 한 번만 실행. SEND ACCEPTED 로그와 smoke@smoke.local 실제 수신을 별도 확인. 실패 시 SMTP 연결 진단; 앱 재배포 금지.

## 실제 결과 분류
정적 release Jenkinsfile에 SEND_RELEASE_MAIL opt-in 추가. 기본 false, VERIFY 모드는 알림 미발송. 정확한 원격 결과/exit code를 확인하고 성공 전환, 합성 롤백 시험, 실제 실패 후 복귀 확인, 미확인을 구분한다. 일반 CI 실패가 롤백 성공을 의미하지 않는다. 메일 실패는 배포 결과를 뒤집거나 트래픽 변경을 재시도하지 않는다. 정적 release는 이미 시험 완료한 과거 fixture 전용이므로 메일 시험 때문에 재실행하지 않는다. 현재 운영 Job이 사용하는 브랜치는 변경하지 않았다. 실제 업무 앱 동적 CD/Release 구현 시 동일한 명시적 결과 계약을 사용하고 커밋/색상/rollback 검증 여부를 추가한다. 제목은 [배포], 시험은 [시험] 또는 [정적시험]으로 식별.

현재 코드 준비 상태: 실제 SMTP 주소, 방화벽 및 경로, 수신 테스트 대기. 운영 배포/ALB 변경 없음. Jenkins Groovy 구문 및 실행 시험은 Jenkins에서 별도 확인.

## VPN 전 임시 경로: SNS → SQS → 사내 메일 (이 절 우선)

- AWS 담당자가 Standard SNS topic ARN과 SQS 연동 완료 여부를 전달한다. Jenkins 전역 환경 변수 SMOKE_DEPLOY_SNS_TOPIC_ARN으로 실제 ARN을 비공개 설정하고 Jenkins EC2 IAM role에는 해당 topic에만 sns:Publish를 허용한다. Jenkins는 SQS 읽기 권한 불필요. KMS 암호화 topic이라면 필요한 제한된 KMS 권한은 AWS 담당자가 검토한다.
- SQS subscription RawMessageDelivery=false 권장: SNS JSON envelope Subject 및 Message를 사용하여 메일 제목/본문 구성. Subject는 [배포]로 시작, Message는 평문 UTF-8, 첫 줄에 Subject와 완전히 동일한 [배포] 제목을 넣고 Event ID를 포함한다. Subject 누락·변형 시 메일 소비자는 Message 첫 줄을 제목으로 복원할 수 있다. SQS 중복 수신 가능하므로 소비자는 MessageId/Event ID 중복 처리, 메일 성공 확인 후 삭제, 실패 시 재시도 및 DLQ를 협의한다. 실제 ARN, 토큰, DB 정보, 내부 URL은 공개 코드나 알림 본문에 넣지 않는다.
- 별도 Job smoke-notice-sns-test, branch */cicd/deployment-mail-notification, script cicd/jenkins/Jenkinsfile.notice-sns-test, CONFIRM_SNS_TEST=true 한 번 실행. 단위 테스트 6개와 SNS acceptance MessageId 확인 후 준호 씨에게 메일 도착 확인. SNS 발행 성공은 최종 수신 성공과 다르다. 전송 상태 불명 시 무조건 재발행하지 않는다.
- 기존 SMTP Job 초안은 VPN 이후 참고용으로 보존; 지금 사용하지 않는다. 정적 release는 SEND_RELEASE_SNS 기본 false, VERIFY 모드는 전송하지 않는다. 정적 release 재실행 없이 독립 Job으로 테스트한다. 동적 업무 앱 release에는 동일 발행기와 정확한 결과 계약을 후속 연동해야 한다. SNS 실패가 ALB rollback을 유발하지 않는다. 실제 Jenkins 설정 및 실행은 미검증.
