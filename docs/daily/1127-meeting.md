# 2026-11-27 · 스모커 프로젝트 DAY 2 일일 회의 및 작업 기록

기준: 17:24 KST 이후 마지막 사용자 제공 터미널 화면, 17:25 AWS 작업일지 및 저장소 조회 main 66d6544. 회의록은 팀원 보고 및 PR 내용의 사후 정리이며 별도 회의 참석/발언 원문을 주장하지 않는다.

## 팀 공통 결정

- 온프레미스 검증 JSP 회사 사이트/공지·자료실을 표준 app/으로 채택(PR #21); Spring Boot 레퍼런스는 app-reference/에 보존. Java 17 WAR notice.war, Tomcat 10.1, boarddb MariaDB 10.11.19.
- 이관 기준: 공지 14, 첨부 메타데이터 1, 문의 6, content_digest 및 file_digest. is_check=1 검증 글은 목록·상세·이관 대조 뷰에서 제외한다.
- RDS DML 전용 boarduser, EFS 공유 RWX PVC smoke-attachments-pvc, /var/smoke/attach, UID/GID 1500, Secret smoke-notice-secret의 DB_PASSWORD/ADMIN_KEY/CHECK_TOKEN. PVC 이름에만 get 허용, Secret 직접 조회 금지. 실제 값은 별도 전달. FILE_BASE_URL 미설정(신규 EFS→S3 동기화 및 CloudFront 완료 전).
- VPN 전 운영 메일: Jenkins → SNS → SQS → 온프레미스 mgmt → smoke@smoke.local. Subject와 Message 첫 줄 동일한 [배포] 제목; RawMessageDelivery=false 권장; 발행 수락과 실제 수신 구분. SNS 권한은 단일 토픽 sns:Publish, 키·ARN 공개 금지.
- 정적 테스트 슬롯과 실제 업무 앱을 구분한다. Blue 100/Green 0 확인 후 Green만 교체; 승인·기능 검증 전 ALB 전환 금지. 최초 전환 후 이전 Blue가 정적이면 업무 롤백으로 평가하지 않음.

## 팀원별 결과

| 담당 | 확인 결과 | 다음 작업 |
| --- | --- | --- |
| 강민서 네트워크 | #14 병합, #26 DAY2 인계 점검. 신규 장비 실측 없음. NET1 구현 근거 보존 | VLAN20 중복/CPU hog, Core2/HSRP 901, 최종 웹→DB/NFS 경로, ACL/VPN/절체/IDS |
| 이준호 서버 | #21 표준 앱 병합; #24 SSH 3대, root 차단, rsyslog TCP514, data 02:00 백업·mgmt 03:00 복제·복구 해시 일치, [백업] 수신, Postfix/Dovecot/Roundcube 문의 알림, Prometheus 3/3·Grafana, 마스킹 캡처 30장(브랜치) | #24 검토, SQS 수신기, 백업 실패 알림, 장애 규칙, 설정 원본 |
| 이우빈 AWS | #27 DAY2 인계 기록; EKS private API/권한, 정적 ALB/TG, ECR 조회 근거. 담당자 보고로 RDS 14/1/6 및 digest 일치, EFS 두 AZ 원본 SHA-256 일치, S3 189525 bytes·SSE-S3·해시 일치. Secret 필수 키 설정, PVC get yes, Secret get no | 실제 앱 연동, SNS/SQS/IAM 인계, HTTPS/CloudFront/EFS→S3, 워커 장애·비용, Terraform/원본 로그 |
| 강찬영 CI/CD | #13/18/19/20/22 병합, 정적 CD·롤백·연속 요청, 최종 JSP 이미지, main CI #8, Plan, #25 실제 Green dry-run 및 patch 적용 | Green rollout/TG 결과 확보, 실제 RDS/EFS/CRUD·원본 다운로드 검증, 동적 실제 앱 release, Poll SCM 복구, #23 SNS 실측 |

## CI/CD 시간순 상세

1. 오전: Java 21 Jenkins 서비스 유지, Java 17 빌드, Maven 3.8.7, Docker 29.10.1, Python 3.12.3. Ansible 2.16.3 / kubectl 1.37.3, EC2 IAM Role + SSH 전용 키, Private API 및 namespace notice 한정. 노드 목록 및 타 namespace 변경 제한. Port-forward RBAC get/create 보완 후 양쪽 HTTP 200.
2. 레퍼런스 앱 CI #1~3 수동, #6 SCM 자동 Docker/ECR 66초, JUnit 10/10, digest 대조. PR #13 병합. 정적 초기 Blue/Green 각각 2 replica, 4 Running, restart 0.
3. CD #1 VERIFY 12초, #2 PLAN 실패(잔류 port-forward), 임시 loopback 포트 및 프로세스 정리 개선 후 #3 PLAN 16초 성공. #4 DEPLOY 11:42:45~11:43:35 50초, Green v3→v4, Blue v2 유지, ALB 변경 없음. PR #18.
4. Release #4 12:03:13~12:04:18, 65초, 전환 검증 22.98초 / 복귀 21.64초. #5 12:05:57~12:07:01, 64초, 20.23초 / 21.56초. 합성 post-switch assertion failure; 실제 Pod 장애는 아님. 별도 180초 연속 HTTP 요청 341/341 성공(Blue 301, Green 40), 실패 0. 원본 CSV 미등록. PR #19.
5. 동적 Plan: 가중치 100/0 및 정확한 Pod/TG IP 매칭, ECR tag/digest·계정 확인, 활성·비활성 슬롯 판별. CI→Plan 별도 handoff #2 99초 성공, executor 반환 후 downstream 호출. Plan #5 39초(로컬 H2 CRUD 22초). 단일 executor 교착을 피하기 위해 main 자동 downstream 미연결. PR #20 병합.
6. 최종 JSP #21 리뷰: /health의 DB/schema/storage, /version, /notices, CHECK_TOKEN 인증, is_check 숨김, 관리자 키 미설정 시 쓰기 제한. PR head b21719b Jenkins 로컬 호환성 및 GitHub App build/MariaDB 성공. #21 병합.
7. 15:42 운영용 이미지 시험: Maven 6.021초, Docker 7.0초, UID/GID 1500, 로컬 볼륨 생성/읽기/해시/삭제, H2 기능 검사 성공. PVC get Forbidden 및 Secret get no 발견; AWS 담당자가 PVC 범위 get만 추가했다고 보고. #22 검사 통과 및 병합.
8. RDS/EFS/S3 원본 이관 및 무결성 대조, Secret 인계는 담당자 보고. CHECK_TOKEN은 Jenkins Secret text credential ID smoke-notice-check-token으로 등록하도록 안내; 실제 등록 확인 없음. DB_PASSWORD·ADMIN_KEY는 K8s Secret에서만 주입.
9. 알림 #23 Draft: SMTP 직접 연결 대신 SNS 발행기로 변경. 발행 성공/실패와 실제 롤백 검증/미확인 구분, 제목/본문 첫 줄 [배포] 동일. SNS 테스트 Job/단위 테스트 작성; 토픽·IAM·실제 수신 대기.
10. 17:13 CI #8 수동 30초: main 66d65449cdf1b0aa585e635b896ec290727a8785, Java17, Maven 6.084초, JUnit 8/8, WAR, numeric user 1500:1500 linux/amd64, H2 UP, ECR push verified. Tag notice-66d65449cdf1b0aa585e635b896ec290727a8785-8; digest sha256:93ea2f76359ffc2aa43932124814a05c1551cdbc7b9d378fa957d0d5676a5dff. Poll SCM 최신 자동 실행은 미확인(#7 오전 이후 수동 #8).
11. 17:15 Plan 19초: Python 8+6+6=20 tests OK, ECR digest 검증, 양쪽 2 Ready/Healthy 및 IP 매칭, ACTIVE_SLOT=blue CANDIDATE_SLOT=green, NEXT_ACTION=PLAN_UPDATE_INACTIVE. CLEANUP UNCONFIRMED는 mocked negative test. 실제 변경 없음.
12. #25 최초 실제 후보 스크립트: 고정 Green, lock, resourceVersion JSON Patch, PVC Bound/RWX, Secret 참조, server dry-run 및 명시적 확인. RDS hostname 오입력으로 1회 차단(변경 없음), 올바른 DB_HOST 재입력 후 5 tests OK 및 GREEN SERVER DRY RUN OK. 17:24 화면에 GREEN PATCH APPLIED 확인. 이후 rollout/TG 검증 결과 미제출. Blue·ALB 수정 요청 없음. Green 실제 앱 정상화/CRUD/RDS/EFS 검증 완료로 기록하지 않음.

## 실행 근거와 공식 점수

main README 스냅샷 66d6544: 전체 10/32(31.2%), 네트워크 1/8, 서버 3/8, AWS 0/8, CI/CD 6/8. 저장소 증빙 기반 지표이며 작업률/완성도와 다르다. #24/#26/#27은 당시 open, #23/#25 Draft. 미병합/미검증 성과로 점수를 올리지 않는다. 실제 업무 앱 CD/Release 실행 근거는 완료 후 별도 등록한다.

## 다음 우선순위

- Green rollout 및 정확한 TG 대상, Pod별 /health/version/list, DB 실연결/스키마, EFS 실물 다운로드 SHA-256 및 숨김 글 CRUD(토큰 비공개) 확인.
- 실제 업무 앱 첫 ALB 전환 승인, 두 실제 버전 확보 후 업무 무중단/자동 롤백/RTO·RPO 시험. 기존 정적 실측을 운영 RTO로 표기하지 않음.
- Jenkins main Poll SCM 복구, CI→CD→Release 연결, 이미지 취약점 검사(Trivy), 선택 승인, 배포 이력은 제안/후속.
- SNS/SQS 수신 시험, VPN/ACL/HTTPS/CloudFront, Redis/EFS→S3 동기화, 워커 장애/비용 실측.
- 원본 연속 CSV 및 안전하게 검수한 CI/CD 캡처 바이너리 추가 제출. 기존 38장 색인은 실제 PNG 업로드와 구분.

## 출처

- [CI/CD WORKLOG](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/blob/main/cicd/WORKLOG.md), [정적 요청 집계](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/blob/main/cicd/verification/1127-alb-continuity-summary.md)
- [#13](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/13), [#18](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/18), [#19](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/19), [#20](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/20), [#21](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/21), [#22](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/22), [#23](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/23), [#25](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/25)
- [서버 #24](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/24), [네트워크 #26](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/26), [AWS #27](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/27), [진행률 #1](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1), [인계 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11)
