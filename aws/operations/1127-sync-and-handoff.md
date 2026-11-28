# 2026-11-27 DAY 2 — 동기화 검증·인계·다음 작업

[작업일지](../WORKLOG.md) · [RDS·EFS·S3 대조](../migration/1127-source-and-target-evidence.md) · [사용자 실행 결과](../verification/1127-recovered-user-results.log) · [인계 Issue #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11)

## 1. 당일 최종 동기화 상태

출처는 「261127 2일차」의 11/27 사용자 메시지다. 검색으로 선별 회수했으며 전체 콘솔 원문·매니페스트 전문을 확보한 것은 아니다.

| 시각 KST | 확인한 결과 | 판정 범위 |
| --- | --- | --- |
| 17:22:05 | 수동 Job Complete 1/1, 소요 24초. 역할 인증과 S3 Sync Start/Complete 로그 조각 | 수동으로 수행한 동기화 Job 성공 |
| 17:22:05 | CronJob schedule `* * * * *`, timezone Asia/Seoul, suspend=True, active 0, LAST SCHEDULE 없음 | 예약은 등록됐지만 자동 실행은 정지 상태 |
| 17:23:21 | 사용자: 후속 작업을 월요일에 하기로 결정 | 남은 시험은 11/30 이후 계획으로 분리 |
| 17:27:40 | CronJob suspend=True, 수동 Job Complete 1/1, Blue/Green 각 2개 Pod Running, PVC Bound/RWX | 사용자 최종 후속 요약. 최종 rollout·대상 그룹 상태·업무 앱 연결은 별도 |

1분 schedule 문자열만으로 1분마다 실제 실행됐거나 RPO가 1분이라고 주장하지 않는다. 수동 동기화 검증과 신규 파일의 정기 동기화 시험도 서로 다르다. 이번 문서화 중 CronJob을 해제하거나 AWS 리소스를 변경하지 않았다.

## 2. 막힌 부분과 후속 해결

| 문제·초기 상태 | 확인된 후속 결과 | 아직 확인할 범위 |
| --- | --- | --- |
| EKS Access Entry와 RoleBinding 그룹 불일치 | 09:18:59 사용자 출력에서 그룹 일치 | 실제 IAM/RBAC 원본 전문 |
| Ansible kubectl 미설치·일부 AWS 조회 거부 | 팀 오전 로그에서 kubectl 1.37.3·private API·notice 권한 확인 | ListClusters 허용까지 완료로 바꾸지 않음 |
| 팀 Port Forward Forbidden | [오전 로그](../../cicd/verification/1127-day2-midpoint.md)의 필요한 subresource 권한·재시험 성공 | 관리용 광범위 권한 부여로 확대하지 않음 |
| 팀 특정 PVC 조회 Forbidden | [오후 로그](../../cicd/verification/1127-day2-afternoon.log)의 PVC BOUND RWX·Green dry-run·17:24 후보 패치 | 최종 후보 앱의 DB·파일 기능 시험 |
| 이관 대상 결과가 1차 게시에 충분히 연결되지 않음 | 11/28 재조회로 RDS·EFS·S3 명령/결과 회수 및 실제 인계 원본 해시 대조 | 미확보 설정 원문을 당시 코드처럼 작성하지 않음 |

## 3. 팀에 전달할 값과 완료 기준

실제 주소·암호·ARN·계정 값은 공개하지 않고 필요한 변수명과 조건만 전달한다. 최신 [DAY2 회의록](../../docs/daily/1127-meeting.md)의 합의 상태를 따른다.

| 주는 사람 → 받는 사람 | 확인한 내용·전달할 조건 | 다음 확인 |
| --- | --- | --- |
| 이준호 → 이우빈 | 원본 14/1/6, 비교 digest, 실제 첨부 1개 189,525 bytes | 원본과 RDS·EFS·S3 대상 대조 결과를 함께 검토 |
| 이우빈 → 강찬영 | RDS boarddb·MariaDB10.11.19, EFS RWX·/var/smoke/attach·UID/GID1500 | 실제 JSP 후보의 조회·첨부 다운로드·쓰기 시험 |
| 이우빈 ↔ 강찬영 | namespace notice, 필요한 PVC 조회, DB_PASSWORD·ADMIN_KEY·CHECK_TOKEN은 실행 시 주입 | Secret 원문 공개 없이 최소 권한으로 후보 배포 검증 |
| 이우빈 ↔ 강찬영·이준호 | FILE_BASE_URL은 신규 동기화·CloudFront 검증 전 미설정 | 동기화와 배포 경로 검증 후 합의해 적용 |

ECR 자동 Push·이미지 digest 및 Jenkins/Ansible 파이프라인은 [CI/CD 담당 기록](../../cicd/WORKLOG.md)을 참조한다. AWS 담당의 ECR 조회 출력은 [별도 발췌](../verification/1127-ecr-images-masked.log)로 유지하고 팀원의 전체 구현 실적으로부터 분리한다.

## 4. 공용 설계와 차이가 있는 항목

- 공통 설계는 HTTPS ALB이지만 당일 직접 확인한 경로는 HTTP였다. 실제 SG의 TCP443 허용만으로 인증서·TLS가 완료된 것으로 보지 않는다.
- 공통 통신 표는 노드 SG를 데이터 계층 출발지로 적었고, 실제 RDS/EFS 캡처는 EKS cluster SG를 표시했다. 워커 연결 SG와 같은 허용 범위인지 팀과 대조하고, 합의 없이 SG를 수정하지 않는다.
- 최초 공통 버전표의 Maven3.9.16·Tomcat11 기준안과 DAY2의 Maven3.8.7·Tomcat10.1 앱 인계 상태가 다르다. Jenkins 서비스 Java21과 앱 빌드 Java17도 구분한다. 실제 값은 회의록·팀 로그를 링크하고 기준안 자체를 AWS 담당 판단만으로 바꾸지 않는다.
- 신규 파일 정기 동기화·CloudFront/OAC·최종 앱 FILE_BASE_URL은 다음 단계다. 현재 S3 익명403과 Versioning Enabled는 독립된 검증 결과다.

## 5. 11/30 이후 다음 작업 순서

1. **이우빈·강찬영:** 실제 Green 후보의 rollout, 대상 그룹 상태, RDS 공지·문의 조회와 EFS 첨부 읽기/쓰기 결과를 확인한다. 정적 test-v2 응답을 업무 앱 성공으로 대신 쓰지 않는다.
2. **이우빈:** 실제 신규 첨부를 기준으로 예약 Job 실행과 S3 대상 해시·지연을 기록한다. 현재 suspend=True라는 상태를 출발점으로 삼고 자동화 해제는 해당 작업 때 수행한다.
3. **이우빈·강찬영:** 도메인·ACM·HTTPS와 CloudFront/OAC를 구축·검증한 뒤 앱 배포 주소·FILE_BASE_URL을 합의한다.
4. **이우빈:** 워커 장애 시 사용자 영향·대체 노드 준비 시간·CloudWatch 관찰·비용을 실제 측정한다. 기존 노드 그룹 존재만으로 AWS4 완료로 처리하지 않는다.

필수 누락 원문은 실제 Terraform, IAM/RBAC, PV/PVC 및 ServiceAccount·CronJob 설정 파일이다. 이미 회수한 실행 명령·출력과 인계 자료를 다시 요구하지 않는다. [진행률 등록](../../docs/progress/evidence.json)은 확인된 구현과 실행 결과만 연결한다.
