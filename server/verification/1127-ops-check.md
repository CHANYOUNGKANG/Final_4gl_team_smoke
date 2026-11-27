# 11/27 온프레미스 운영 기능 확인 기록 · 이준호

직접 실행하고 화면으로 확인한 결과만 적는다. 캡처는 관리 주소를 지운 사본이다 ([evidence/2026-11-27](../evidence/2026-11-27/)). 화면 출력을 글자로 옮긴 사본은 [logs/1127-terminal-transcript.md](../logs/1127-terminal-transcript.md), 재구축 순서·명령은 [docs/1127-rebuild-guide.md](../docs/1127-rebuild-guide.md). 공개 자료의 주소는 `MGMT_HOST`·`WEB_HOST`·`DATA_HOST`·`MAIL_RELAY_HOST` 로 표기한다.

| 서버 | 이 기록에서 확인한 역할 |
| --- | --- |
| mgmt | Ansible 중앙 관리 · 중앙 로그 수신 · 백업 사본 보관 · Prometheus/Grafana |
| web | Nginx → Tomcat 회사 사이트·공지 자료실 · Postfix/Dovecot/Roundcube 메일 |
| data | MariaDB `boarddb` · NFS 첨부 저장소(LVM) · 백업 생성 |

## 1. Ansible 중앙 관리

- inventory 그룹 `mgmt`(local)·`web`·`data`, 상위 그룹 `servers` — [그림 01](../evidence/2026-11-27/1127-01-ansible-inventory-masked.png)
- 3대 `/etc/hosts` 에 `mgmt.smoke.local`·`web.smoke.local`(`mail.smoke.local`)·`data.smoke.local` 등록 — [그림 02](../evidence/2026-11-27/1127-02-ansible-hosts-masked.png)
- `ansible servers -m ping` 3대 응답, 공통 플레이북 PLAY RECAP `failed=0` — [그림 03](../evidence/2026-11-27/1127-03-ansible-ping-masked.png) · [그림 04](../evidence/2026-11-27/1127-04-ansible-common-recap-masked.png)

## 2. SSH 정책 (SRV1)

Ansible 로 3대에 `/etc/ssh/sshd_config.d/10-smoke.conf` 를 배포한 뒤 `sshd -T` 로 실제 적용값을 확인했다 — [그림 05](../evidence/2026-11-27/1127-05-ssh-policy-3hosts-masked.png)

```
# mgmt · web · data 모두 같은 값 (sshd -T 출력)
maxauthtries 3
permitrootlogin no
allowusers rocky
```

- 처음에는 설치 시 생성된 `01-permitrootlogin.conf` 가 먼저 읽혀 `PermitRootLogin yes` 가 유지됐다 → 해당 파일 제거 후 위 값 확인
- mgmt 에서 web 으로 `ssh root@WEB_HOST` 시도 → 접속 경고 문구 표시 후 `Permission denied`, web 로그에 `Failed password for invalid user root` 기록 — [그림 06](../evidence/2026-11-27/1127-06-ssh-root-blocked-masked.png)

## 3. 중앙 로그 수집 (SRV1)

web·data 의 rsyslog 가 TCP 514 로 mgmt 에 전달하고, mgmt 는 `/var/log/remote/<호스트>/<프로그램>.log` 로 나눠 저장한다.

- web·data 에서 `logger -t smoke-test` 실행 → mgmt `/var/log/remote/{data,web}/smoke-test.log` 에 각 1줄 (11:11:09) — [그림 07](../evidence/2026-11-27/1127-07-central-log-masked.png)
- 위 2절의 root 접속 실패 기록도 mgmt `/var/log/remote/web/sshd-session.log` 에서 조회

## 4. 저장소 분리와 공유

- data: 첨부 5G(`/share`) · DB 4G(`/var/lib/mysql`) LVM 분리, 예비 10G 디스크 — [그림 08](../evidence/2026-11-27/1127-08-data-lvm-disk-masked.png) · [그림 09](../evidence/2026-11-27/1127-09-data-lvm-lvs-masked.png)
- NFS: `/share/attach` 를 web 대역과 임시 NAT 대역에만 공유(`all_squash`, `anonuid/anongid=1500`), web `/var/smoke/attach` 마운트 5.0G — [그림 10](../evidence/2026-11-27/1127-10-nfs-export-mount-masked.png)
- web fstab 은 `_netdev,nofail` 로 data 가 늦게 떠도 부팅이 멈추지 않게 했다

## 5. 회사 사이트·공지 자료실과 이관 기준값

- Nginx(80) → Tomcat(127.0.0.1:8080) 회사 사이트 — [그림 11](../evidence/2026-11-27/1127-11-web-homepage-masked.png)
- 첨부 업로드 시 DB `board_file.sha256` 저장, NFS 실제 파일 `sha256sum` 과 일치 — [그림 12](../evidence/2026-11-27/1127-12-board-attach-sha256-masked.png)
- `v_migration_check` 기준값(게시글·첨부·문의 건수, 본문·첨부 목록 해시) 조회 — [그림 13](../evidence/2026-11-27/1127-13-migration-baseline-masked.png). 인계 수집(14:04) 기준 게시글 14 · 첨부 1 · 문의 6

## 6. 백업·복구 (SRV2)

플레이북: [configuration/ansible/backup.yml](../configuration/ansible/backup.yml)

- data `/backup/YYYYMMDD-HHMM/` 에 `boarddb.sql.gz`·`migration_check.txt`·`attach-sha256.txt`·`attach.tar.gz`·`SHA256SUMS` 생성 — [그림 14](../evidence/2026-11-27/1127-14-backup-data-masked.png)
- mgmt `/backup/data/` 로 복제 — [그림 15](../evidence/2026-11-27/1127-15-backup-copy-mgmt-masked.png)
- cron: data 02:00 백업, mgmt 03:00 복제 — [그림 16](../evidence/2026-11-27/1127-16-backup-cron-masked.png)
  - sudo 로 실행한 rsync 가 root 의 known_hosts 를 찾아 호스트 키 확인에 실패 → `UserKnownHostsFile` 을 rocky 의 파일로 지정해 해결
- 복구 시험: 덤프를 임시 DB 에 복원해 게시글·첨부·문의 건수와 본문 해시 앞 16자리가 원본과 같고, 첨부 해시 확인 OK — [그림 17](../evidence/2026-11-27/1127-17-restore-test-masked.png)

## 7. 사내 메일 (SRV4)

```
# web: postconf (mynetworks 값은 사내 대역으로 가림)
myhostname = mail.smoke.local
mydomain = smoke.local
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain
home_mailbox = Maildir/
message_size_limit = 20971520
```

- Postfix 로컬 배달 `status=sent`, `Maildir/new` 에 메일 파일 생성 — [그림 21](../evidence/2026-11-27/1127-21-mail-postfix-delivery-masked.png)
- Dovecot 2.3.21 IMAP. Roundcube 가 `user@smoke.local` 형식으로 로그인해 인증이 실패 → `auth_username_format = %Ln` 로 해결 — [그림 22](../evidence/2026-11-27/1127-22-mail-dovecot-masked.png)
- Roundcube 1.7.0 (`/webmail/`, `public_html` 만 공개) 로그인, user1 → user2 송수신 — [그림 23](../evidence/2026-11-27/1127-23-webmail-login-masked.png) · [그림 24](../evidence/2026-11-27/1127-24-webmail-inbox-masked.png) · [그림 25](../evidence/2026-11-27/1127-25-webmail-user2-masked.png)

## 8. 운영 알림 메일 수신 (SRV4)

| 알림 | 보내는 곳 | 받는 곳 | 결과 |
| --- | --- | --- | --- |
| 홈페이지 문의 | web Tomcat(`MAIL_TO`) | smoke@smoke.local | 문의 #7 접수 → 메일 수신 (12:50) — [그림 26](../evidence/2026-11-27/1127-26-contact-form-masked.png) · [그림 27](../evidence/2026-11-27/1127-27-contact-mail-masked.png) |
| 백업 성공·실패 | data `smoke-backup-notify.sh` → web Postfix 25 | smoke@smoke.local | `[백업] data 성공` 수신 (16:20) — [그림 18](../evidence/2026-11-27/1127-18-backup-mail-ansible-masked.png) · [그림 19](../evidence/2026-11-27/1127-19-backup-mail-cron-masked.png) · [그림 20](../evidence/2026-11-27/1127-20-backup-mail-inbox-masked.png) |
| 배포 결과·롤백 | Jenkins(AWS) → SNS → SQS → mgmt 수신 | smoke@smoke.local | **미확인** — SQS·수신 스크립트 준비 전 |
| AWS 장애 | CloudWatch → SNS → SQS | smoke@smoke.local | **미확인** |
| 공격 탐지 | Snort(GNS3) | smoke@smoke.local | **미확인** — 네트워크 연동 전 |

- 백업 메일: Ansible 실행 `changed=2 failed=0`(래퍼 배포·cron 교체), data 에서 래퍼 직접 실행 `rc=0`, cron `0 2 * * * /usr/local/bin/smoke-backup-notify.sh`
- 메일 본문에 백업 폴더·크기·파일 5개 목록 포함. 실패하면 제목이 `[백업] data 실패(rc=N)` 로 바뀌고 실행 로그 마지막 20줄이 붙는다 (실패 경로는 아직 시험하지 않음)

## 9. 모니터링

- 3대 node_exporter(9100, 관리 대역만 허용) → mgmt Prometheus → Grafana(Node Exporter Full)
- Prometheus Target health `3 / 3 up` — [그림 28](../evidence/2026-11-27/1127-28-monitoring-targets-masked.png)
- web 대시보드, data 디스크별(`/share`·`/var/lib/mysql`) 사용량 — [그림 29](../evidence/2026-11-27/1127-29-monitoring-web-masked.png) · [그림 30](../evidence/2026-11-27/1127-30-monitoring-data-masked.png)
- 장애 알림 규칙(디스크·서버 다운 → 메일)은 아직 만들지 않음
