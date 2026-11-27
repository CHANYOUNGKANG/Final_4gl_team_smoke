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
