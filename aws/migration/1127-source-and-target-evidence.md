# 2026-11-27 DAY 2 — RDS·EFS·S3 이관과 원본 대조

담당: 이우빈 · AWS, 원본 인계: 이준호 · 서버. 11/28에 DAY2 사용자 실행 결과를 추가 회수해 원래 작업 날짜에 보완했다. **실제 인계 파일**, **회수한 사용자 명령·출력**, **팀원 로그**, **미확인 항목**을 구분한다. 이번 정리에서 AWS에 새로 접속하거나 이관을 재실행하지 않았다.

[사용자 명령·출력 발췌](../verification/1127-recovered-user-results.log) · [원본 기준값](../verification/1127-handoff-source-baseline-masked.log) · [콘솔 상태](../infrastructure/1127-console-configuration.md) · [작업일지](../WORKLOG.md)

## 1. 목적·환경·실행 위치

온프레미스 게시글·첨부·문의 데이터를 보존하면서 AWS 앱이 사용할 DB와 파일 저장소를 준비했다. RDS MariaDB는 DB 대상, EFS는 두 AZ의 Pod가 같은 첨부를 사용하는 RWX 저장소, S3는 첨부 객체 보관·후속 배포 경로다. 개별 데이터 이관과 최종 JSP 앱의 조회·다운로드 통합 시험은 별도다.

실제 RDS 복원은 Terraform EC2의 `ec2-user`, 작업 디렉터리 `~/smoke-db/handoff-20261127-1404`에서 수행한 것으로 회수됐다. EFS 파일 전송은 같은 EC2에서 `kubectl exec`로 두 시험 Pod에 접근했고, S3 해시는 같은 인계 디렉터리에서 AWS CLI로 확인했다. Kubernetes 인증 정보·실제 IAM 정책 전문은 미확보이므로 최소 권한 전체를 적용했다고 단정하지 않는다. DB 인증 값·관리 주소·객체 식별자는 공개하지 않는다.

## 2. 실제 확보한 원본과 기준값

| 항목 | 확인한 값·출처 |
| --- | --- |
| 실제 인계 원본 | handoff-20261127-1404.tar.gz, 192,494 bytes |
| 원본 내부 수집 시각 | 2026-11-27 14:04:54 KST |
| 프로젝트 첨부 업로드 시각 | 2026-11-27 15:46:56 KST |
| 원본 MariaDB | 10.11.19-MariaDB |
| 기준 건수 | notice/board 14, file/board_file 1, inquiry 6 |
| 첨부 | 1개, 189,525 bytes |
| 원본 자체 대조 | sha256_missing 0, DB 기록 해시와 실제 파일 해시 일치, 06_diff.txt 0 bytes |

원본의 `03_counts.txt`, `04_v_migration_check.txt`, `05_attach-sha256.txt`, `06_db-sha256.txt`, `06_result.txt`, `08_storage_info.txt`를 확인했다. 원본 DB 덤프·사용자 첨부 JPG·인계 압축파일은 공개하지 않는다.

별도 첨부 `schema.sql` 원본 4,029 bytes를 직접 확보했고, 최신 main의 [app/sql/schema.sql](../../app/sql/schema.sql)과 바이트가 같았다. SHA-256은 `ec874791855709f6353c45b6ff14c79061bedca359f1663963c4f0de34241704`다. 팀원이 작성한 DDL은 기존 공용 소스를 링크하며 AWS 폴더에 중복 복제하지 않았다. 실제 실행 여부는 아래 사용자 mysql 결과로 구분했다.

## 3. 16:19:48 — RDS 복원과 데이터 대조

출처: 파이널 프로젝트 DAY2 대상 검색에서 회수한 **2026-11-27 16:19:48 KST 사용자 메시지**. 이 RDS 검색 결과에는 원제목이 별도로 반환되지 않았다. 전체 세션이 아닌 선별 발췌다. [검증 로그](../verification/1127-recovered-user-results.log)에 실제 명령 순서와 결과를 보존했다.

1. gzip·sed 명령으로 덤프의 sandbox 지시문과 특정 DEFINER 구문을 제거해 `boarddb-rds-restore.sql`을 생성했다. 이는 명령의 역할 설명이며, 별도 오류 원문 없이 특정 에러가 발생했다고 만들지 않았다.
2. RDS에 복원 SQL을 입력하고 종료 코드 **0**을 확인했다.
3. 같은 DB에 `~/smoke-db/schema.sql`을 적용하고 종료 코드 **0**을 확인했다.
4. 접속 출력에서 **10.11.19-MariaDB-log managed by https://aws.amazon.com/rds/**를 확인했다.
5. `SELECT * FROM v_migration_check\G` 결과를 실제 인계 원본의 동일 기준값과 대조했다.

아래는 회수한 실제 mysql 명령이다. 원문 옵션을 유지하고 DB 사용자만 `$DB_USER`로 치환했다. `-p`는 대화식 암호 입력이며 비밀번호 자체는 없다.

```bash
mysql -h "$RDS_ENDPOINT" -P 3306 -u "$DB_USER" --ssl-ca="$HOME/rds-certs/global-bundle.pem" --ssl-verify-server-cert --default-character-set=utf8mb4 -p boarddb < boarddb-rds-restore.sql
mysql -h "$RDS_ENDPOINT" -P 3306 -u "$DB_USER" --ssl-ca="$HOME/rds-certs/global-bundle.pem" --ssl-verify-server-cert --default-character-set=utf8mb4 -p boarddb < ~/smoke-db/schema.sql
```

CA 파일과 서버 인증서 검증 옵션을 사용하는 복원 명령이다. 인증서 파일·비밀번호·복원용 데이터 SQL은 공개하지 않는다. 복원용 SQL 파일 전체를 새로 만들어 당시 원본이라고 표시하지 않았다.

| v_migration_check 항목 | 인계 원본 | RDS 사용자 출력 | 11/28 자료 대조 |
| --- | --- | --- | --- |
| notice_count | 14 | 14 | 일치 |
| file_count | 1 | 1 | 일치 |
| inquiry_count | 6 | 6 | 일치 |
| content_digest | 아래 값 | 아래 값 | 64자리 전체 일치 |
| file_digest | 아래 값 | 아래 값 | 64자리 전체 일치 |

```text
content_digest=1a9ce447409e695b3306bb3daa1b2af5f4d5931fa8df4cfc12aa7d364be80544
file_digest=cc910c6c5d02be3e11867f710030f628d0a49e650f2dd17553611a5d7be2f878
```

이 두 digest는 비교 뷰의 결과이며 아래 첨부 JPG 자체의 SHA-256과 다르다. 같은 기준의 뷰 결과가 일치한 범위로 기록하고 모든 DB 객체·권한·업무 화면을 검증했다고 확대하지 않는다.

## 4. 15:16:14 공유 시험 → 16:25:58 실제 첨부 EFS 이관

처음 공유 시험에서는 PV **5Gi / RWX / Retain**, PVC **Bound**, 2a·2c 시험 Pod의 공유 쓰기가 회수됐다. 시험 파일의 SHA-256은 `68b45b66a9c938759983c83685bb46bca842644a835836fadd70094028dc27a5`다. **이 파일은 실제 이관 첨부와 다른 시험 파일이다.**

16:25:58에는 인계 첨부를 tar 표준 출력으로 꺼내 2a 시험 Pod에 기록한 명령과 종료 코드 **0**을 확인했다. 같은 파일을 두 Pod에서 조회한 결과는 다음과 같다.

| 확인 항목 | 2a 시험 Pod | 2c 시험 Pod |
| --- | --- | --- |
| 파일 크기 | 189,525 bytes | 189,525 bytes |
| 소유 UID:GID | 1500:1500 | 1500:1500 |
| 파일 모드 | -rw-r----- | -rw-r----- |
| SHA-256 | 아래 원본 첨부 해시 | 같은 해시 |

```text
069a3999ebd30bab566730c80d0e4a8f227250d13634235dcfa0ce3e876a3120
```

실제 명령의 `umask 027`·`set -C`와 두 Pod의 sha256sum 순서는 [공개용 발췌](../verification/1127-recovered-user-results.log)에 있다. 원본 파일 이름은 `<ATTACHMENT_FILE>.jpg`로 치환했다. 이 표시는 기록용 자리표시자이며 그대로 실행하는 스크립트가 아니다. PV/PVC·시험 Pod YAML 전문을 어시스턴트 제안으로 재구성하지 않았다.

## 5. 16:35:22 — S3 객체와 다운로드 해시

사용자 `head-object` 결과는 **AES256 / 189525 / image/jpeg**였다. S3 객체를 표준 출력으로 내려받아 계산한 SHA-256은 위 실제 첨부 해시와 일치했다. 검색에서 생략된 `aws s3 cp`의 옵션을 제안 명령으로 채우지 않고 [검증 로그](../verification/1127-recovered-user-results.log)에 부분 명령과 결과를 구분했다.

11/28 자료 정리 중 실제 인계 압축파일 내부의 JPG 바이트를 읽어 SHA-256을 새로 계산했다. 다음 네 값이 모두 같았다.

| 대조 대상 | 크기·결과 |
| --- | --- |
| 실제 인계 JPG 바이트의 새 해시 계산 | 189,525 bytes, 069a3999…76a3120 |
| 원본 05_attach-sha256.txt | 전체 64자리 일치 |
| 원본 06_db-sha256.txt | 전체 64자리 일치 |
| 회수한 사용자 S3 다운로드 출력 | 전체 64자리 일치 |

이는 **실제 인계 원본과 회수된 사용자 실행 출력의 대조**다. 이번에 S3에 접속해 재다운로드했다는 뜻이 아니다. [버킷](../evidence/1127-s3-bucket-masked.png)과 [객체](../evidence/1127-s3-object-masked.png) 화면도 기존 경로에서 확인할 수 있다.

## 6. 17:08:11 — S3 보안 상태

실제 사용자 명령·결과에서 Public Access Block의 네 항목이 모두 true, Versioning은 Enabled, 익명 객체 HTTPS 요청은 **HTTP Status: 403**이었다. 명령 전체는 [검증 로그](../verification/1127-recovered-user-results.log)에 있다. 이는 S3 원본 직접 접근 차단이며 **ALB HTTPS·인증서·CloudFront/OAC 완료 증거가 아니다.**

## 7. 17:22 이후 — 수동 동기화와 보류한 자동 시험

[운영·다음 작업](../operations/1127-sync-and-handoff.md)에 최종 상태를 정리했다. 수동 Job은 Complete 1/1이지만 CronJob은 suspend=True, LAST SCHEDULE 없음이었다. 17:23:21 사용자 지시에 따라 후속 시험은 월요일로 미뤘고 17:27:40 후속 요약에서도 suspend=True가 유지됐다. 1분 예약 실행·신규 파일 자동 동기화·RPO 1분 달성을 완료로 기록하지 않는다.

## 8. 다음 검증과 자료 한계

| 남은 항목 | 필요한 특정 자료·완료 기준 |
| --- | --- |
| 실제 업무 앱 통합 | 최종 Green rollout·target health, RDS 공지/첨부 조회와 EFS 다운로드 결과 |
| 신규 첨부 자동 동기화 | 새 첨부 생성 시각, 실제 예약 Job 실행 시각, S3 대상 해시·지연 측정 |
| CloudFront/OAC | 원본 비공개 상태를 유지한 배포 경로와 앱 FILE_BASE_URL 인계·다운로드 시험 |
| 재현용 설정 원문 | 실제 사용한 Terraform, PV/PVC, ServiceAccount·CronJob·IAM 설정 원문. 값은 가린 사본만 |

이미 확보한 RDS 명령·대상 결과, EFS/S3 해시, 인계 압축파일·스키마·캡처를 다시 요청하지 않는다. 1차 점검에서 대상 원문을 회수하지 못해 보류했던 부분은 이번 후속 자료로 갱신했고, [당시와 현재의 차이](../operations/1128-progress-review.md)를 보존했다.
