# 2026-11-28 AWS 게시 기록·진행률 재점검

## 2차 재정리 — 부분 구현 기준과 새 실행 근거 반영

이 절이 최신 판정이다. 11/28 20:16 KST 정리 기준으로 프로젝트 DAY2 대상 검색에서 회수한 **11/27 사용자 실행 메시지**와 실제 첨부 원본을 대조했다. 1차 재점검 때 조회되지 않았던 두 AZ 노드·RDS·EFS·S3 결과가 이후 검색에서 확인됐다. 기존 “검색 불가”와 0점 판단은 아래에 당시 이력으로 보존한다. 새로 실행한 AWS 작업으로 날짜를 바꾸지 않는다.

사용자가 다시 제공한 「스모커 팀 프로젝트 GitHub 통합 관리 및 작업물 업로드 지침」 9절은 **0점 미구현, 1점 부분 구현, 2점 완료 기준과 실행 검증 근거 충족**을 명시한다. 1차 판단은 전체 완료 조건을 부분 구현 1점에도 요구해 실제 HTTP ALB 등의 진척을 너무 엄격하게 제외했다. 이 해석을 정정하고, [팀 기준](../../docs/progress/README.md)의 콘솔 구성 증거 등록과 [계산 코드](../../tools/progress/report.py)를 그대로 사용한다.

단순 완료 보고나 어시스턴트 제안을 검증 성공으로 올리지 않는다. 이번 추가 근거는 검색 결과가 **USER의 실제 명령·출력**으로 식별한 값이며, [회수 기록](../verification/1127-recovered-user-results.log)에 원래 대화 제목·메시지 시각·생략 범위를 표시한다. 전체 원문 로그나 Terraform·IAM·PV/PVC·CronJob YAML 전문을 확보했다고 주장하지 않는다. 반환되지 않은 명령 인자와 출력 행도 새로 복원하지 않는다.

## 새로 확인한 실행 결과와 원본 대조

| 작업 날짜·메시지 시각 (KST) | 확인한 사용자 실행 결과 | 판정과 제한 |
| --- | --- | --- |
| 11/27 09:17:41 | 실제 노드 조회에서 두 노드 모두 Ready, AZ는 각각 ap-northeast-2a/2c. Pod 6개 Running·재시작 0 | 두 AZ EKS 기반의 실행 근거. 실제 EKS 조회를 DB subnet group 화면으로 대신하지 않음 |
| 11/27 09:18:59 | Access Entry 그룹이 smoke-deployers로 확인돼 RoleBinding과 일치 | 09:17의 smoke-deployment 불일치 이후 수정 결과. 어시스턴트 제안 명령을 실제 실행 원문으로 바꾸지 않음 |
| 11/27 11:05:34 | Helm v4.3.2, chart 3.6.2 설치 명령, STATUS deployed / REVISION 1 | 차트 버전과 Controller 이미지/App version을 구분. 잘린 출력에서 Deployment/Pod Ready를 추정하지 않음 |
| 11/27 16:19:48 | RDS 복원·스키마 적용 종료 코드 0, RDS 서버 버전 출력, 건수 14/1/6과 두 비교 digest | 실제 인계 압축파일의 기준값·digest와 일치. 원본 온프레미스 숫자만으로 RDS 성공을 만든 것이 아님 |
| 11/27 16:25:58 | 실제 첨부 전송 종료 코드 0, EFS의 2a/2c에서 189,525 bytes·1500:1500·동일 SHA-256 | 실제 인계 첨부 해시와 일치. 15:16 공유 쓰기 시험의 다른 파일 해시와 구분 |
| 11/27 16:35:22 | S3 객체 AES256·189,525 bytes·image/jpeg, 재다운로드 SHA-256 | 실제 인계 첨부 해시와 일치 |
| 11/27 17:08:11 | Public Access Block 4개 true, Versioning Enabled, 익명 직접 접근 403 | 해당 S3 보안·접근 검증. CloudFront 또는 전체 앱 검증으로 확대하지 않음 |
| 11/27 17:22:05·17:27:40 | 수동 S3 동기화 Job Complete 1/1, CronJob suspend=True. 후속 출력에서 Blue/Green 각 Pod 2개 Running, PVC Bound/RWX | 수동 실행 성공과 예약 자동 실행을 구분. 최종 rollout·대상 그룹·실제 앱의 RDS/EFS 연동 성공은 별도 미확인 |

17:23:21의 사용자 메시지는 제안된 다음 작업을 월요일로 미뤘다. CronJob 예약 실행, 신규 파일의 자동 동기화와 전체 업무 앱 연결을 완료로 쓰지 않는다. 명령·결과의 공개용 회수 기록은 원래 순서를 유지하며 민감 식별자만 치환한다.

## 이번 AWS 등록과 실제 로컬 계산

| 이정표 | 구현 등록 | 실행 등록 | 기존 계산기 로컬 결과 | 남은 범위 |
| --- | --- | --- | --- | --- |
| AWS1 두 AZ의 EKS 기반 | [실제 EKS 구성·접근 기록](../infrastructure/1127-eks-access-and-controller.md) | [사용자 노드·Pod 출력 회수](../verification/1127-recovered-user-results.log) | 2/2 | 이 점수는 EKS 기반에 한정. 업무 앱 통합·워커 장애 시험을 포함하지 않음 |
| AWS2 ALB HTTPS와 전환·복귀 | [실제 HTTP ALB·두 대상 그룹 구성](../infrastructure/1127-console-configuration.md) | 등록하지 않음 | 1/2 | 부분 구현. HTTPS 리스너·인증서·TLS 응답이 확인되지 않음 |
| AWS3 게시글·첨부 데이터 이관 | [실제 이관 명령·대상 연결](../migration/1127-source-and-target-evidence.md) | [RDS·EFS·S3 대조 결과 회수](../verification/1127-recovered-user-results.log) | 2/2 | 이 점수는 확인된 데이터 이관·대조에 한정. CloudFront·전체 업무 앱·예약 동기화 검증을 포함하지 않음 |
| AWS4 워커 교체와 장애 관찰 | 등록하지 않음 | 등록하지 않음 | 0/2 | 장애 주입·워커 교체·사용자 영향·모니터링 실측 미확인 |

**기존 report.py를 실제 실행해 AWS 5/8점(62.5%), 팀 전체 19/32점(59.4%)을 확인했다.** 최신 main 2f5ce3a5의 팀원 변경을 포함한 계산이다. 네트워크1·서버7·AWS5·CI/CD6점이며 계산 코드 변경은 없다. 이 문서를 작성하는 시점에는 새 커밋의 원격 검사·main 반영 전이다. PR 검사와 병합 후 main·Issue #1을 재조회한 결과는 해당 PR과 인계 이슈에 남긴다.

기존 AWS1의 11/26 부분 관찰 파일과 작업일지는 보존한다. 이번 등록은 **09:17:41의 실제 두 AZ Ready 결과가 새로 확인됐기 때문에** 완료 실행 근거를 갱신한 것이다. 부분 verification에 implementation만 덧붙여 근거 없이 2점으로 올린 것이 아니다. AWS2에는 implementation만 등록해 1점 부분 구현을 명확히 한다.

## 게시 이력과 동시 변경 보존

- 1차 보완은 [PR #27](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/27)에서 11/28 **19:47:40 KST에 병합**됐다. 병합 커밋은 [3f2df280](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/3f2df280f3f6ac7268561a8426175958bbdd85c6), 당시 담당 브랜치 커밋은 [676387ef](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/676387efbe6949942ac47acb11cc98de16975ed2)다. 18개 파일 반영을 확인했으며, 1차의 0점 판단과 이번 후속 정정을 구분한다.
- 2차 준비 중 서버의 [PR #30](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/30)이 main에 병합됐다. [2f5ce3a5](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/2f5ce3a5c356f0f39a107a16e7611ce6d2f15d74)를 다시 읽어 SRV1·SRV2·SRV3와 CICD1·CICD2 등록을 원문 그대로 보존하고 AWS 항목만 갱신한다.
- main 패널과 자동 README 영역을 손으로 고치지 않는다. 담당 브랜치의 새 PR·검사·병합과 main 실제 반영은 실행 후 결과로 보고한다.

---

## 1차 재점검 이력 — 당시 자료·0점 판단 보존

아래는 PR #27 보완 때의 수집 범위와 판단이다. 당시 검색 오류·미확보 항목·0점 유지는 이력이며, 현재 확인 상태는 위 2차 재정리와 실제 로컬 계산을 따른다.

### 확인한 문제

점검 시작 기준 `main`은 `117c29702998b68471fa0cc56e727821fce2b87e`, 담당 브랜치는 `81a95ce7422a1cd765b5128661bdc9cb8712a9c5`였다. [PR #27](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pull/27)은 파일 4개가 올라간 열린 PR이며 당시 main에 병합되지 않았다.

기존 PR의 [PR check](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/runs/45965697195), [Secret scan](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/runs/45965697490), [Team progress](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/runs/45965683256)는 이미 성공했다. “검사 대기”는 재점검 당시 상태와 맞지 않았다. 이 보완 커밋은 별도로 새 검사를 받아야 한다.

### 점수가 올라가지 않은 계산 경로

[팀 기준](../../docs/progress/README.md)과 [실제 계산 코드](../../tools/progress/report.py)를 대조했다.

- main 패널·Issue #1은 main의 자료를 기준으로 한다. 담당 브랜치에만 있는 변경은 그 브랜치 Actions 실행 요약에 표시된다.
- Markdown의 일반 문장·표는 자동 구현 분석 대상이 아니며 fenced 코드 블록을 분석한다. `.log`는 구현 자동 분석 확장자에서 제외된다.
- 수동 `implementation`은 실제 콘솔 구성·설정 내보내기·캡처를 사용할 수 있다. Terraform 파일만 허용되는 것은 아니다.
- 현재 `AWS1`에는 부분 관찰에 대한 `verification`만 있다. 구현 근거가 없으면 계산식상 0점이다. AWS2~4 등록은 없다.
- `implementation`과 `verification`이 모두 있으면 2점이 된다. “부분 검증”이라는 문구가 점수를 제한해 주지는 않으므로, 전체 기능에 맞는 실행 근거인지 먼저 확인해야 한다.
- 수동 근거는 유효한 다른 파트 원문을 링크할 수도 있다. 팀원의 파일을 복사하거나 기여자를 바꿀 필요는 없다.

**기존 PR을 그대로 병합하는 것만으로 AWS 점수는 오르지 않는다.** 게시 반영 누락과 이정표 증빙 부족은 각각 해결해야 한다.

### 이번에 확보한 실제 진척과 공식 이정표

| 공식 이정표 | 직접 확인 자료 / 보존된 관찰 | 아직 부족한 범위 | 이번 점수 처리 |
| --- | --- | --- | --- |
| AWS1 두 AZ의 EKS 기반 | 11/26 노드 2대 Ready·시스템 Pod 6개 회수 요약, 실제 두 AZ VPC 화면, 팀 Ansible 접근 검증 | 실제 EKS 구성과 연결 서브넷, 노드별 AZ 원문. DB subnet group 두 AZ를 EKS 증거로 대체할 수 없음 | 0/2 유지 |
| AWS2 ALB HTTPS와 전환·복귀 | 실제 HTTP 리스너, Blue/Green 각각 Healthy 2개, 정적 HTTP 응답, 팀 전환·복귀 로그 | HTTPS 리스너·인증서 구성 및 실제 TLS 응답 | 0/2 유지 |
| AWS3 게시글·첨부 데이터 이관 | 실제 인계 원본의 14/1/6·파일 기준값, RDS/EFS 대상 구성, S3 동일 이름 객체 | 실제 이관 명령·구현 원문, RDS 대상 데이터·파일 해시 대조 원문 | 0/2 유지 |
| AWS4 워커 교체와 장애 관찰 | 기존 기반·계획 기록 | 워커 장애·대체 준비·사용자 영향·모니터링 실측 | 0/2 유지 |

실제 구축 작업이 없다는 뜻이 아니다. 현재 지표는 대표 이정표의 **저장소 증빙**을 세므로, 확인된 부분 작업은 [AWS 현황](../README.md), [11/27 작업일지](../WORKLOG.md), [구성 캡처](../infrastructure/1127-console-configuration.md), [이관 근거](../migration/1127-source-and-target-evidence.md)와 함께 평가해야 한다. 임의 완료율을 만들거나 점수 패턴에 맞추기 위한 미실행 코드를 추가하지 않았다. `evidence.json`과 공통 계산 코드는 변경하지 않았다.

### 이번 보완 범위

- 11/27 실제 첨부 25장, 스키마, ECR 원문, 인계 압축파일의 비데이터 메타자료를 확인했다.
- 성공·구성 상태가 표시된 실제 화면 9장을 골라 식별자를 제거한 사본으로 추가했다. 생성 전 양식은 완료 증거로 쓰지 않았다.
- 인계 원본 기준값과 RDS 복원 후 결과의 차이를 문서화했다.
- 팀의 오후 PVC 검증·Green 후보 패치 성공을 연결해 이전 오류만 현재 상태로 남지 않게 했다. 최종 rollout/target health는 확인하지 못한 상태를 유지했다.
- 원래 작업 날짜는 11/27이며, 11/28의 새 AWS 구축 실적으로 반복 기록하지 않았다.
- 최신 main의 팀원 변경과 기존 담당 브랜치 이력을 보존한 뒤 같은 PR에서 검사·병합 상태를 확인한다. 결과는 해당 PR 및 인계 이슈에 남긴다.

### 수집 범위와 접근 한계

2026-11-28 저녁 KST에 프로젝트 첨부 원본과 GitHub main·담당 브랜치·PR·팀 로그를 재조회했다. 이전 대화의 실제 검색 기능은 이번 대화에서 사용할 수 없다는 오류를 반환했다. 따라서 모든 대화나 11/28의 모든 AWS 작업을 열람했다고 보장하지 않는다. 기존에 회수한 사용자 결과는 출처 종류를 유지해 보존한다. 검색되지 않은 작업을 미수행·실패로 판정하지 않는다.

앞으로 기록할 때는 실행 날짜, 원래 대화 제목·메시지 시각(조회 가능할 때), 첨부 업로드 시각, 원문 여부, 실제 실행 주체를 구분한다. 공식 점수와 확인된 부분 진척을 함께 제공하고, 점수가 바뀌지 않았으면 이유와 필요한 특정 증거를 적는다.
