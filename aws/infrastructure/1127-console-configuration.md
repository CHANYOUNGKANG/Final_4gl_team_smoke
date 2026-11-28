# 2026-11-27 AWS 콘솔 구성 증빙

11월 27일 프로젝트 첨부 원본을 11월 28일 다시 확보해 확인했다. 아래 시각은 **첨부 업로드 시각(KST)**이며, 원래 대화 메시지 시각이나 리소스 생성 시각으로 바꾸어 쓰지 않는다. 실제 리소스 식별자·계정·관리 주소를 불투명하게 제거한 사본만 공개한다.

[작업일지](../WORKLOG.md) · [진행률 판정](../operations/1128-progress-review.md) · [공통 아키텍처](../../docs/architecture/README.md)

## ALB와 두 대상 그룹

| 실제 관찰 | 원본 / 업로드 시각 | 공개 증빙 | 범위 |
| --- | --- | --- | --- |
| Blue 대상 그룹: IP 대상, HTTP 8080, 대상 2개 Healthy | image(20261127-023628).png / 11:36:27 | [Blue](../evidence/1127-alb-blue-targets-masked.png) | 해당 화면의 대상 상태 |
| Green 대상 그룹: IP 대상, HTTP 8080, 대상 2개 Healthy | image(20261127-023642).png / 11:36:41 | [Green](../evidence/1127-alb-green-targets-masked.png) | 해당 화면의 대상 상태 |
| ALB HTTP 주소에서 정적 test-v2 응답 | image(20261127-023848).png / 11:38:47 | [HTTP 응답](../evidence/1127-alb-http-response-masked.png) | 정적 시험 앱 접속. 실제 게시판·HTTPS 검증과 구분 |
| 저장된 HTTP:80 리스너의 Blue 100 / Green 0 전달 설정 | image(20261127-024508).png / 11:45:07 | [리스너](../evidence/1127-alb-http-listener-masked.png) | 그 시점의 전달 구성. 전환·복귀 전 과정은 별도 로그 |

후속 전환·복귀는 CI/CD 담당자의 [Release #5 실행 기록](../../cicd/verification/1127-notice-release-build-5-rollback.log)을 연결한다. Blue/Green 각각 Healthy 2개, 전환 확인 20.23초, 의도적 assertion 실패 후 복귀 확인 21.56초, 최종 Blue 100 / Green 0이다. [연속 조회 집계](../../cicd/verification/1127-alb-continuity-summary.md)는 341/341 PASS, 실패 0, Blue 301 / Green 40을 기록한다. 이는 정적 시험과 합성 실패의 결과이며 실제 업무 앱·TLS·워커 장애나 모든 순간의 무중단을 증명하지 않는다. 원본 CSV는 이번에 확보하지 못했다.

AWS 대상 그룹·권한과 CI/CD 파이프라인·검증은 공동 연동 결과다. 팀원의 Jenkins·Ansible 구현을 AWS 담당자의 단독 구현 실적으로 바꾸지 않는다.

## RDS와 EFS

| 실제 관찰 | 원본 / 업로드 시각 | 공개 증빙 | 범위 |
| --- | --- | --- | --- |
| DB subnet group에 ap-northeast-2a / ap-northeast-2c | image(20261127-032947).png / 12:29:46 | [DB 서브넷 그룹](../evidence/1127-rds-subnet-group-masked.png) | DB 서브넷 그룹의 두 AZ. EKS 워커 두 AZ 실행 증거와 구분 |
| EFS Access Point 1개 사용 가능, POSIX UID/GID 1500:1500 | image(20261127-055926).png / 14:59:25 | [Access Point](../evidence/1127-efs-access-point-masked.png) | Access Point 상태. 경로 전체는 화면에서 잘렸으며 실제 마운트·쓰기·읽기와 두 AZ mount target은 별도 |
| RDS MariaDB 사용 가능, db.t3.micro, ap-northeast-2c, 3306, 퍼블릭 액세스 아니요, 서브넷 2개 | image(20261127-061901).png / 15:19:00 | [RDS](../evidence/1127-rds-instance-masked.png) | 인스턴스와 연결 설정. 엔진 세부 버전·DB 복원·데이터 대조 결과는 이 화면에 없음 |

실제 실행한 Terraform 파일 전체, IAM/RBAC·PV/PVC 원문은 이번 자료에서 확보하지 못했다. 새 코드를 작성해 기존 실행 파일로 표시하지 않았다. [공통 IP·통신 허용표](../../docs/architecture/ip-plan.md)는 설계이고, 위 콘솔 화면은 각 시점에 확인된 실제 상태다. 이번 문서 작업으로 인프라·소프트웨어·주소를 바꾸지 않았다.

## 저장된 보안 그룹 규칙 — 11/28 추가 회수

아래 3장은 편집·생성 전 입력 양식이 아니라 저장된 인바운드 규칙 화면이다. 기존 9장은 그대로 재사용했다.

| 실제 관찰 | 원본 / 업로드 KST | 공개 증빙 | 한계 |
| --- | --- | --- | --- |
| ALB HTTP/TCP80·HTTPS/TCP443 2개 규칙 | image(20261127-021437).png / 11:14:36 | [ALB SG](../evidence/1127-alb-security-group-masked.png) | 소스 열은 화면 밖. TLS·인증서·HTTPS 접속 성공과 구분 |
| RDS TCP3306 2개 규칙 | image(20261127-033214).png / 12:32:13 | [RDS SG](../evidence/1127-rds-security-group-masked.png) | 원본 소스 SG를 대조해 Bastion SG와 EKS cluster SG로 확인. DB 복원 성공은 별도 |
| EFS NFS/TCP2049 1개 규칙 | image(20261127-034554).png / 12:45:53 | [EFS SG](../evidence/1127-efs-security-group-masked.png) | 원본 소스 SG는 EKS cluster SG. 실제 공유 읽기·쓰기는 별도 |

원본과 사본에서 마스크 밖 픽셀이 같고, 가린 부분은 불투명 검정이며 PNG 부가 메타데이터를 제거했다. 공개본에서 지운 실제 SG 식별자는 다시 적지 않는다. 공용 설계의 노드 SG와 실제 cluster SG의 연결 관계는 [인계에서 대조할 항목](../operations/1127-sync-and-handoff.md)으로 남긴다.

## 이후 인계 상태

기존 [UID/GID 1500 이미지 점검](../../cicd/verification/1127-production-image-1500.log)의 PVC 조회 Forbidden은 당시 경과로 보존한다. 이후 [11/27 오후 팀 실행 기록](../../cicd/verification/1127-day2-afternoon.log)에 `PVC BOUND RWX VERIFIED`, `GREEN SERVER DRY RUN OK`, 17:24 KST `GREEN PATCH APPLIED`가 기록됐다.

위 팀 로그의 확인 범위는 PVC 검증과 격리된 Green 후보 패치 적용까지다. 추가 회수한 사용자 17:27:40 후속에는 Blue/Green 각 2개 Pod Running, PVC Bound/RWX가 있다. [사용자 결과](../verification/1127-recovered-user-results.log)를 함께 보되 Running을 readiness·rollout·대상 그룹 최종 성공으로 확대하지 않는다. ALB 자동 전환은 없으며 최종 rollout·target health·업무 앱의 RDS/EFS 통합 성공은 같은 로그에서 아직 관찰되지 않았다. 이전 PVC 오류만 현재 상태로 반복하지 않고 후속 성공과 남은 검증을 함께 기록한다.

## 완료 증빙에 사용하지 않은 화면

원본은 확인했으나 다음 화면은 생성·설치 전 입력 양식이므로 완료 증빙으로 올리지 않았다.

- ALB의 두 AZ 선택 입력 화면
- EFS의 두 AZ mount target 생성 입력 화면
- EFS CSI v3.6.0-eksbuild.1의 “설치 준비 완료” 화면
- S3의 Public Access Block·버전 관리·SSE-S3 생성 입력 화면
- S3 sync Pod Identity의 생성 버튼 이전 화면

보안 그룹에서 443을 허용한 사실과 HTTPS 리스너·인증서가 실제 동작하는 사실은 별도다. 현재 확보 자료만으로 AWS2 전체 완료를 판정하지 않는다.

## 실행 결과와 연결

이 문서는 실제 캡처가 증명하는 범위만 설명한다. 추가 회수한 EKS 두 AZ 실행·Helm 설치는 [EKS 인계](1127-eks-access-and-controller.md), RDS·EFS·S3 실제 명령과 원본 무결성 대조는 [이관 기록](../migration/1127-source-and-target-evidence.md)에 있다. 화면에 없는 성공을 이미지 자체의 증거로 표시하지 않는다.
