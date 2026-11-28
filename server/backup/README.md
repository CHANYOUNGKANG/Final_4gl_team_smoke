# 백업·복구

[← 서버 파트](../README.md) · 플레이북 [backup.yml](../configuration/ansible/backup.yml) · 확인 기록 [11/27 §6](../verification/1127-ops-check.md#6-백업복구-srv2)

## 구성

| 시각 | 서버 | 하는 일 |
| --- | --- | --- |
| 02:00 | data | `smoke-backup-notify.sh` → `smoke-backup.sh` 실행 → 결과 메일 `[백업] data 성공/실패` 를 smoke@smoke.local 로 |
| 03:00 | mgmt | data `/backup/` 을 `/backup/data/` 로 복제 (rsync, rocky 키) |

백업 폴더 `/backup/YYYYMMDD-HHMM/` (7일 보관)

| 파일 | 내용 | 쓰임 |
| --- | --- | --- |
| `boarddb.sql.gz` | `mysqldump --single-transaction --routines --triggers` | 복구·RDS 이관 원본 |
| `migration_check.txt` | `v_migration_check` 결과 (건수·본문/첨부 목록 해시) | 이관 후 대조 기준 |
| `attach-sha256.txt` | 첨부 파일별 SHA-256 | 복구·S3 이관 후 파일 대조 |
| `attach.tar.gz` | 첨부 원본 | 복구 |
| `SHA256SUMS` | 위 파일들의 해시 | 백업 파일 손상 확인 |

## 왜 이렇게 했나

- 백업을 원본과 같은 서버에만 두면 서버 장애 때 함께 사라진다 → mgmt 에 한 벌 더
- 백업은 복구돼야 의미가 있다 → 임시 DB 복원으로 건수·해시를 원본과 비교
- 조용히 실패하면 모른다 → 매일 결과를 메일로 통보, 실패 시 로그 첨부
- 검증된 백업 스크립트는 그대로 두고 메일은 감싸는 스크립트(래퍼)로만 추가

## 복구 시험 순서

```bash
# data: 최신 백업을 임시 DB 에 복원해 원본과 비교
B=$(ls -1d /backup/2* | tail -1)
(cd "$B" && sha256sum -c SHA256SUMS)
sudo mysql -e "CREATE DATABASE boarddb_restore"
zcat "$B/boarddb.sql.gz" | sudo mysql boarddb_restore
# 원본(boarddb)과 복원본의 v_migration_check 건수·해시 비교 후 임시 DB 삭제
sudo mysql -e "DROP DATABASE boarddb_restore"
```

## 남은 일

- 실패 메일 경로 시험 (일부러 실패를 만들어 `[백업] data 실패` 수신 확인)
- 메일함(Maildir) 백업 범위 결정
