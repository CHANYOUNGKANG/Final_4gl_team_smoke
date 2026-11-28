# 2026-11-27 · 스모커 프로젝트 DAY 2 회의록 및 작업보고 (최종 정리)

| 구분 | 내용 |
| --- | --- |
| 프로젝트 | DevOps 기반 고가용성 가상화 MSA 시스템 구축 — 공지·자료실 인프라 전환 |
| 작업일 | 2026-11-27 금요일, DAY 2 |
| 사후 검수 기준 | 2026-11-28 20:24 KST, main `80044e8`, PR #30·#31·#32 반영 |
| 팀 구성 | 강민서(네트워크/보안·PM), 이준호(서버/메일), 이우빈(AWS), 강찬영(CI/CD) |
| 기록 성격 | 팀원 보고·저장소 실행 자료의 통합 작업보고. 실제 회의 참석 여부·회의 장소·발언 원문은 확인되지 않아 기재하지 않음 |

## 1. 요약 및 공식 진행률

DAY2의 핵심 성과는 표준 JSP 앱 확정, 온프레미스 운영 기능 구축, AWS 데이터 이관·무결성 확인, 정적 Blue/Green 배포 및 자동 복귀 시험이다. 실제 JSP 후보는 Green 패치까지 진행했고 최종 업무 기능 및 전환은 남아 있다. 11/28 문서 보완은 11/27 실적에 귀속하며 새 구축으로 중복 계산하지 않는다.

| 담당 | DAY2 당시 main 66d6544 | 11/28 최신 공식 점수 | 증빙 |
| --- | ---: | ---: | --- |
| 강민서 · 네트워크 | 1/8 | 1/8 (12.5%) | [DAY1](../../network/verification/1126-day1.md), [#26](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/26) |
| 이준호 · 서버 | 3/8 | 7/8 (87.5%) | [#30](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/30), [검증표](../../server/verification/1127-ops-check.md) |
| 이우빈 · AWS | 0/8 | 5/8 (62.5%) | [#27](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/27), [#31](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/31), [#32](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/32) |
| 강찬영 · CI/CD | 6/8 | 6/8 (75.0%) | [실행 기록](../../cicd/WORKLOG.md) |
| 합계 | 10/32 (31.2%) | **19/32 (59.4%)** | [공식 Issue #1](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1) |

9점 상승은 뒤늦게 반영된 서버·AWS 증빙을 포함한 집계 변화이며 하루 동안 실제 전체 작업의 28.2%를 새로 구축했다는 뜻은 아니다. 1점은 핵심 구현, 2점은 이정표 실행 검증까지 충족. 남은 시간과 전체 요구사항 완성도는 별도다. AWS는 0→3→5점으로 정정되었다.

## 2. 팀 공통 결정 및 인계 기준

- 온프레미스 검증 JSP 회사 사이트/공지·자료실을 표준 app/으로 채택(PR #21); Spring Boot 레퍼런스는 app-reference/에 보존. Java 17 WAR notice.war, Tomcat 10.1, boarddb MariaDB 10.11.19.
- 이관 기준: 공지 14, 첨부 메타데이터 1, 문의 6, content_digest 및 file_digest. is_check=1 검증 글은 목록·상세·이관 대조 뷰에서 제외한다.
- RDS DML 전용 boarduser, EFS 공유 RWX PVC smoke-attachments-pvc, /var/smoke/attach, UID/GID 1500, Secret smoke-notice-secret의 DB_PASSWORD/ADMIN_KEY/CHECK_TOKEN. PVC 이름에만 get 허용, Secret 직접 조회 금지. 실제 값은 별도 전달. FILE_BASE_URL 미설정(신규 EFS→S3 동기화 및 CloudFront 완료 전).
- VPN 전 운영 메일: Jenkins → SNS → SQS → 온프레미스 mgmt → smoke@smoke.local. Subject와 Message 첫 줄 동일한 [배포] 제목; RawMessageDelivery=false 권장; 발행 수락과 실제 수신 구분. SNS 권한은 단일 토픽 sns:Publish, 키·ARN 공개 금지.
- 정적 테스트 슬롯과 실제 업무 앱을 구분한다. Blue 100/Green 0 확인 후 Green만 교체; 승인·기능 검증 전 ALB 전환 금지. 최초 전환 후 이전 Blue가 정적이면 업무 롤백으로 평가하지 않음.

실제 환경 기준은 Jenkins 서비스 Java 21, 앱 Java 17, Maven 3.8.7, Tomcat 10.1, MariaDB 10.11.19이다. 초기 설계 기준과 차이는 공통 인계 이슈에서 정리한다. LBC Helm chart 3.6.2는 컨트롤러 이미지 버전이 아니다. 네트워크 설계 변경/제외 여부는 별도 팀 합의 전 확정하지 않는다.

## 3. 담당자별 작업 및 검증

### 3.1 강민서 — 네트워크·보안 (1/8)

- 11/26 Core1의 VLAN 10/20/30/40/901, SVI, rapid-PVST, HSRPv2 구성과 관리 서버 방향 ICMP 5/5, pfSense 인접 WAN 응답 2건을 기존 증빙으로 유지한다.
- 11/27 PR #26은 DAY2 인계 점검 및 미검증 목록 정리이며 신규 장비 실측은 없다. 현재 열린 PR로 확인되며 main에는 #14의 기존 자료가 반영돼 있다.
- VLAN20 중복 주소, VMware/GNS3 L2 이중 경로, CPU hog, Core2/HSRP 901은 미해결 또는 재확인 대상. 최종 web→data TCP3306·NFS2049 경로, ACL/NAT/VPN, 절체, IDS 로그 시험은 미검증.
- 다음 작업: 중복 IP/MAC과 경로를 대조하고 최종 통신망을 서버 담당과 확정한다. 범위 축소는 팀 승인 후 요구사항과 함께 수정한다.

근거: [WORKLOG](../../network/WORKLOG.md), [DAY1 검증](../../network/verification/1126-day1.md), [PR #26](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/26).

### 3.2 이준호 — Linux 서버·운영 (7/8)

| 영역 | 11/27 결과 | 남은 범위 |
| --- | --- | --- |
| 중앙 관리 | mgmt/web/data 3대 Ansible ping 성공, 공통 플레이북 failed=0 | 실제 운영 원본 정리 |
| SSH | 3대 PermitRootLogin no, AllowUsers rocky, MaxAuthTries 3. root 로그인 차단 | 최종 네트워크에서 접근 검증 |
| 중앙 로그 | web/data → mgmt rsyslog TCP514, 시험 로그 각 1줄 및 root 실패 기록 수신 | IDS/AWS 연계 |
| 저장소 | DB LVM 4G, 첨부 5G 분리, NFS 마운트 5G, UID/GID 1500 | 최종 통신 경로 재검사 |
| 웹 서비스 | Nginx→Tomcat JSP 공지·자료실, 첨부 SHA 확인, #21 표준 앱 확정 | 팀 표준 최신 WAR 재검증 |
| 백업 | data 백업 및 mgmt 복제, 임시 DB 복구와 첨부 SHA 일치 | 02:00/03:00 예약 실행 및 실패 알림 실측 |
| 메일 | Postfix/Dovecot/Roundcube 송수신, 문의 알림 12:50, 백업 성공 메일 16:20 | SQS·CloudWatch·Jenkins·Snort 수신 |
| 모니터링 | Prometheus 3/3 up, Grafana web/data 대시보드 | 장애 알림 규칙·수신 검증 |

트러블슈팅: SSH 설정 우선순위 문제, rsync known_hosts 불일치, Roundcube 사용자명 형식 문제를 해결한 기록이 있다. #30은 #24를 대체하여 병합됐으며 11/27 공개 캡처 30장, 설정 예시/재구성본, 검증표, 재구축 가이드가 main에 있다. 자동 예약 실행 및 실패 메일은 수동 성공과 구분한다.

근거: [검증표](../../server/verification/1127-ops-check.md), [재구축 가이드](../../server/docs/1127-rebuild-guide.md), [캡처](../../server/evidence/2026-11-27/), [PR #30](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/30).

### 3.3 이우빈 — AWS 클라우드·이관 (5/8)

| 시각 KST | 수행 및 검증 결과 |
| --- | --- |
| 09:17:41 | EKS 워커 2대 Ready, 각각 ap-northeast-2a/2c, 시스템 Pod 6 Running·재시작 0 |
| 09:18:59 | Access Entry와 RoleBinding 그룹 일치 후속 출력. 팀 Ansible private API, notice RBAC 검증 |
| 11:05:34 | Helm v4.3.2, LBC chart 3.6.2 설치 deployed/revision 1, 후속 Deployment 2/2 회수 |
| 오전~점심 | ALB HTTP80 가중치 100/0, 각 TG Healthy 2, 정적 HTTP 응답. 팀과 전환·복귀 시험 |
| 15:16:14 | EFS PV 5Gi/RWX/Retain, PVC Bound, 두 AZ 공유 쓰기 확인 |
| 16:19:48 | RDS MariaDB 10.11.19 복원 및 schema 적용 각각 exit 0. 건수·두 digest 일치 |
| 16:25:58 | 실제 첨부 EFS 이관 exit 0, 두 AZ 동일 189,525 bytes, UID/GID 1500, SHA-256 일치 |
| 16:35:22 | S3 객체 AES256/image/jpeg/189,525 bytes, 재다운로드 SHA-256 원본과 일치 |
| 17:08:11 | S3 PAB 4개 true, Versioning Enabled, 익명 직접 접근 HTTP403 |
| 17:22:05 | 수동 동기화 Job Complete 1/1, 24초; CronJob suspend=True, 예약 실행 이력 없음 |
| 17:27:40 | 각 슬롯 Pod 2개 Running, PVC Bound/RWX 후속 회수. 최종 JSP rollout/TG/기능 미검증 |

11/26 구축한 VPC 2AZ·6서브넷·RT4·IGW·NAT1 및 SG 기반을 사용했다. 11/27 공개 캡처는 기존 9장+SG 3장으로 12장(전체 AWS 19장). SG 화면에서 ALB TCP80/443, RDS3306 두 규칙, EFS2049 확인. 가려진 출발지 식별자는 별도 확인한다. 443 허용과 HTTPS 인증서 적용은 별개다.

**이관 대조:** 초기 온프레미스 임시 복구 캡처는 14/1/2, 14:04:54 인계 기준 및 RDS는 14/1/6. 게시글·파일 목록 digest와 실제 JPG의 전체 SHA-256 일치. 동일 파일의 크기 189,525 bytes. 이전 공유 시험 파일 해시와 실제 이관 첨부 해시는 구분한다.

**판정:** AWS1 2/2, AWS2 1/2, AWS3 2/2, AWS4 0/2. HTTPS·CloudFront/OAC, 예약 동기화, 실제 JSP 연동, 워커 장애/교체·CloudWatch·비용은 미검증. Terraform/IAM/RBAC/PV/PVC/CronJob 실제 원본 일부 미확보. #32의 사용자 명령·출력 선별 회수와 원본 대조는 새 AWS 재실행이 아니다.

근거: [AWS WORKLOG](../../aws/WORKLOG.md), [실행 발췌](../../aws/verification/1127-recovered-user-results.log), [이관 대조](../../aws/migration/1127-source-and-target-evidence.md), [운영 인계](../../aws/operations/1127-sync-and-handoff.md), [PR #32](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/32).

### 3.4 강찬영 — CI/CD (6/8)

1. 오전: Java 21 Jenkins 서비스 유지, Java 17 빌드, Maven 3.8.7, Docker 29.10.1, Python 3.12.3. Ansible 2.16.3 / kubectl 1.37.3, EC2 IAM Role + SSH 전용 키, Private API 및 namespace notice 한정. 노드 목록 및 타 namespace 변경 제한. Port-forward RBAC get/create 보완 후 양쪽 HTTP 200.
2. 레퍼런스 앱 CI #1~3 수동, #6 SCM 자동 Docker/ECR 66초, JUnit 10/10, digest 대조. PR #13 병합. 정적 초기 Blue/Green 각각 2 replica, 4 Running, restart 0.
3. CD #1 VERIFY 12초, #2 PLAN 실패(잔류 port-forward), 임시 loopback 포트 및 프로세스 정리 개선 후 #3 PLAN 16초 성공. #4 DEPLOY 11:42:45~11:43:35 50초, Green v3→v4, Blue v2 유지, ALB 변경 없음. PR #18.
4. Release #4 12:03:13~12:04:18, 65초, 전환 검증 22.98초 / 복귀 21.64초. #5 12:05:57~12:07:01, 64초, 20.23초 / 21.56초. 합성 post-switch assertion failure; 실제 Pod 장애는 아님. 별도 180초 연속 HTTP 요청 341/341 성공(Blue 301, Green 40), 실패 0. 원본 CSV 미등록. PR #19.
5. 동적 Plan: 가중치 100/0 및 정확한 Pod/TG IP 매칭, ECR tag/digest·계정 확인, 활성·비활성 슬롯 판별. CI→Plan 별도 handoff #2 99초 성공, executor 반환 후 downstream 호출. Plan #5 39초(로컬 H2 CRUD 22초). 단일 executor 교착을 피하기 위해 main 자동 downstream 미연결. PR #20 병합.
6. 최종 JSP #21 리뷰: /health의 DB/schema/storage, /version, /notices, CHECK_TOKEN 인증, is_check 숨김, 관리자 키 미설정 시 쓰기 제한. PR head b21719b Jenkins 로컬 호환성 및 GitHub App build/MariaDB 성공. #21 병합.
7. 15:42 운영용 이미지 시험: Maven 6.021초, Docker 7.0초, UID/GID 1500, 로컬 볼륨 생성/읽기/해시/삭제, H2 기능 검사 성공. PVC get Forbidden 및 Secret get no 발견; AWS 담당자가 PVC 범위 get만 추가했다고 보고. #22 검사 통과 및 병합.
8. RDS/EFS/S3 원본 이관 및 무결성 대조는 #32의 사용자 실행 발췌 및 원본 대조로 보완됐다. Secret 인계는 담당자 보고이며 실제 값은 기록하지 않는다. CHECK_TOKEN은 Jenkins Secret text credential ID smoke-notice-check-token으로 등록하도록 안내; 실제 등록 확인 없음. DB_PASSWORD·ADMIN_KEY는 K8s Secret에서만 주입.
9. 알림 #23 Draft: SMTP 직접 연결 대신 SNS 발행기로 변경. 발행 성공/실패와 실제 롤백 검증/미확인 구분, 제목/본문 첫 줄 [배포] 동일. SNS 테스트 Job/단위 테스트 작성; 토픽·IAM·실제 수신 대기.
10. 17:13 CI #8 수동 30초: main 66d65449cdf1b0aa585e635b896ec290727a8785, Java17, Maven 6.084초, JUnit 8/8, WAR, numeric user 1500:1500 linux/amd64, H2 UP, ECR push verified. Tag notice-66d65449cdf1b0aa585e635b896ec290727a8785-8; digest sha256:93ea2f76359ffc2aa43932124814a05c1551cdbc7b9d378fa957d0d5676a5dff. Poll SCM 최신 자동 실행은 미확인(#7 오전 이후 수동 #8).
11. 17:15 Plan 19초: Python 8+6+6=20 tests OK, ECR digest 검증, 양쪽 2 Ready/Healthy 및 IP 매칭, ACTIVE_SLOT=blue CANDIDATE_SLOT=green, NEXT_ACTION=PLAN_UPDATE_INACTIVE. CLEANUP UNCONFIRMED는 mocked negative test. 실제 변경 없음.
12. #25 최초 실제 후보 스크립트: 고정 Green, lock, resourceVersion JSON Patch, PVC Bound/RWX, Secret 참조, server dry-run 및 명시적 확인. RDS hostname 오입력으로 1회 차단(변경 없음), 올바른 DB_HOST 재입력 후 5 tests OK 및 GREEN SERVER DRY RUN OK. 17:24 화면에 GREEN PATCH APPLIED 확인. 이후 rollout/TG 검증 결과 미제출. Blue·ALB 수정 요청 없음. Green 실제 앱 정상화/CRUD/RDS/EFS 검증 완료로 기록하지 않음.

## 4. 공동 검증 지표

| 측정 항목 | 관찰 결과 | 한계 |
| --- | --- | --- |
| 정적 CD #4 | 50초, Green v3→v4, Blue v2 유지 | 실제 JSP 배포 아님 |
| Release #4 | 전환 확인 22.98초, 자동 복귀 확인 21.64초 | 합성 검사 실패 |
| Release #5 | 전환 확인 20.23초, 자동 복귀 확인 21.56초 | 합성 검사 실패 |
| 정적 연속 HTTP | 약 180초, 341/341 PASS, 실패 0, Blue 301/Green 40 | 샘플 관측, CSV 원본 대기; 절대 무중단/RTO 아님 |
| CI→Plan | 별도 handoff 99초, child 13 tests, 성공 | main 영구 자동 체인 미검증 |
| 최종 앱 CI #8 | 수동 30초, Maven 6.084초, JUnit 8/8, ECR digest 일치 | 최신 main SCM 자동 검증 대기 |
| 17:15 Plan | 19초, 20 tests, 슬롯·TG 일치 | 읽기 전용 |
| 실제 Green | 5 tests, PVC Bound/RWX, server dry-run, 17:24 patch applied | 최종 rollout/health·DB/EFS·업무 전환 대기 |
| 데이터 이관 | RDS 14/1/6 및 두 digest 일치, EFS/S3 원본 SHA 일치 | 최종 업무 앱 통합은 별도 |
| 온프레미스 | Ansible 3대, Prometheus 3/3, root 차단, 백업 복원·메일 성공 | 장애/배포/보안 통합 알림 대기 |

[정적 연속 요청](../../cicd/verification/1127-alb-continuity-summary.md) · [Release #5](../../cicd/verification/1127-notice-release-build-5-rollback.log) · [오후 로그](../../cicd/verification/1127-day2-afternoon.log).

## 5. 이정표 전체 점수표 (공식 16개)

| ID | 점수 | 확인된 근거 / 추가 조건 |
| --- | ---: | --- |
| NET1 | 1/2 | VLAN·라우팅 기반 / 최종 통신 및 절체 |
| NET2 | 0/2 | 방화벽 허용·차단 검증 대기 |
| NET3 | 0/2 | 본사·지사 VPN 검증 대기 |
| NET4 | 0/2 | IDS·로그 연동 대기 |
| SRV1 | 2/2 | SSH 정책·중앙 로그 실행 |
| SRV2 | 2/2 | 백업·복구·원본 대조 |
| SRV3 | 2/2 | 온프레 JSP WAR 실행, 표준 앱 빌드 기반 |
| SRV4 | 1/2 | 메일 기반 및 일부 수신 / 통합 장애·배포·보안 알림 |
| AWS1 | 2/2 | EKS 2AZ Ready·실행 |
| AWS2 | 1/2 | HTTP ALB 및 전환 / HTTPS와 업무 통합 |
| AWS3 | 2/2 | RDS/EFS/S3 실제 이관 대조 |
| AWS4 | 0/2 | 워커 교체·장애 관찰 |
| CICD1 | 2/2 | 레퍼런스 SCM 자동 WAR 및 최종 JSP 빌드 |
| CICD2 | 2/2 | 자동 ECR 및 digest / 최신 JSP 자동 증빙 보완 |
| CICD3 | 1/2 | 정적 후보 배포 및 실제 Green 패치 / 업무 앱 최종 확인 |
| CICD4 | 1/2 | 정적 전환·롤백 / 실제 업무 앱 전환·복귀 |
| 합계 | 19/32 | 59.4% |

## 6. 다음 작업 계획 (11/30 월요일, 제안 순서)

| 우선 | 주 담당 / 협업 | 작업 및 완료 기준 |
| --- | --- | --- |
| P0 | 강찬영·이우빈 | Green rollout, readiness, TG IP 매칭, Pod별 health/version, RDS 조회, EFS 실제 다운로드 SHA 및 숨김 검증 글 생성·조회·삭제. 실패 시 ALB 미변경 |
| P0 | 강찬영 | main Poll SCM 최신 자동 빌드 확인, CI→Plan→CD→Release 연결 검증. 두 실제 앱 버전 확보 후 승인 전환·실패 자동 복귀 및 원본 연속 요청 CSV |
| P0 | 이준호·강민서 | 최종 web/data/NFS 경로·주소, SSH/ACL·VPN, 중복 IP·L2 문제 해결 및 측정 |
| P1 | 이우빈 | 신규 파일 예약 동기화 시험(현재 suspend=True), HTTPS/ACM, CloudFront/OAC, FILE_BASE_URL 합의 |
| P1 | 이준호·이우빈·강찬영 | SNS→SQS→mgmt→운영 메일: 동일 테스트 건 발행·수신 시간 대조. 백업 실패 및 장애 알림 시험 |
| P2 | 이우빈·강찬영 | 워커 장애 주입 전 승인·백업, 요청 실패 수·ASG 대체 시간·CloudWatch·비용 측정 |
| P2 | 강민서·이준호 | IDS/보안 로그·운영 알림 검증 |
| 공통 | 전원 | 실제 설정 원본·마스킹 캡처·CSV·PR 근거 보완, 발표 자료 연결 |

실제 앱 정상화 및 데이터 검증 전 ALB 전환 금지. 최초 전환 후 이전 Blue가 정적 앱이면 업무 롤백 시험으로 인정하지 않는다. 11/30~12/07 통합·장애 검증, 12/07~12/09 보고/발표 일정은 기존 WBS 기준이다. 우선순위는 기술 의존성에 따른 제안이며 별도 팀 확정 회의 발언은 아니다.

## 7. GitHub 반영 및 자료 한계

- #24는 #30으로 대체 병합, #27·#28·#31·#32 병합. #23·#25 draft open, #26 open. 미병합 코드와 이미 관찰된 실행 결과는 구분한다.
- AWS #32의 16개 변경 blob은 main과 일치하며 PR/Secret scan/main progress 성공을 확인했다. [#32](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/32) · [공식 점수](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1).
- AWS 공개 이미지 19장 전수는 이전 및 이번 감사에서 직접 판독했다. 서버 30장은 저장소 검증표와 관련 캡처 3장을 대조했으나 전체 30장을 직접 재판독하지 않았다. CI/CD 38장 인덱스는 등록됐지만 PNG 바이너리·연속 CSV 원본은 미등록이다.
- 원래 회의 녹취·전원 발언, 새 AWS/서버/장비 접속 실측은 없다. 제출 로그·마스킹 이미지·원본 대조 보고에 근거한 문서이며 실제 비밀값은 포함하지 않는다.
- [일일 요약](1127.md) · [통합 결과표](../delivery/README.md#결과-기록표) · [인계 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11) · [운영 알림 #29](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/29).
