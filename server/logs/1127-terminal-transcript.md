# 11/27 터미널 출력 옮겨 적기 · 이준호

[가린 캡처](../evidence/2026-11-27/)에 나온 출력을 글자로 옮겼다. 검색과 인용을 쉽게 하려는 사본이며, 원본 화면은 각 캡처다. 주소·계정은 변수 이름으로 바꿨다. 직접 실행해 화면으로 확인한 것만 적었다.

## 1. SSH 정책 적용값 (mgmt·web·data, `sudo sshd -T`) — 그림 05

```
maxauthtries 3
permitrootlogin no
allowusers rocky
```

## 2. 백업 결과 메일 래퍼 배포 (mgmt, `ansible-playbook backup.yml`) — 그림 18

첫 실행 (실패)

```
TASK [백업 + 메일 알림 래퍼] ****
fatal: [data]: FAILED! => {"changed": false, "msg": "Could not find or access 'templates/smoke-backup-notify.sh.j2' ... on the Ansible Controller."}
PLAY RECAP ****
data : ok=3  changed=1  unreachable=0  failed=1  skipped=0  rescued=0  ignored=0
```

원인: mgmt `~/ansible` 에 `templates/`·`group_vars/` 폴더가 없었다. 두 파일을 만든 뒤 다시 실행했다.

두 번째 실행 (성공)

```
TASK [dnf] ****                     ok: [data]
TASK [백업 스크립트] ****            ok: [data]
TASK [백업 + 메일 알림 래퍼] ****    changed: [data]
TASK [매일 02:00 실행] ****          changed: [data]
PLAY RECAP ****
data : ok=5  changed=2  unreachable=0  failed=0  skipped=0  rescued=0  ignored=0
```

`[WARNING]: Found both group and host with same name: web / data / mgmt` 는 mgmt 의 실제 inventory 에서 그룹과 호스트 이름이 같아서 나온 안내다. 동작에는 영향이 없다. 저장소의 [예시 inventory](../configuration/ansible/inventory.example.ini)는 그룹 이름을 `*_servers` 로 달리 두었다.

## 3. 래퍼 직접 실행과 cron (data) — 그림 19

```
$ sudo /usr/local/bin/smoke-backup-notify.sh; echo rc=$?
s-nail: Obsoletion warning: Use of old-style credentials, which will vanish in v15!
rc=0
$ sudo crontab -l
#Ansible: smoke-backup
0 2 * * * /usr/local/bin/smoke-backup-notify.sh
```

노란 경고는 s-nail 의 SMTP 주소 표기 방식 안내이고 발송에는 영향이 없다. `-S v15-compat` 옵션 추가는 다음 작업으로 남긴다 (적용 여부 미확인).

## 4. smoke@ 메일함에 도착한 백업 결과 (Roundcube) — 그림 20

```
제목: [백업] data 성공          보낸 사람: backup@smoke.local   2026-11-27 16:20
서버: data
시작: 2026-11-27 16:20:41 / 종료: 2026-11-27 16:20:41
결과: 성공
백업 폴더: /backup/20261127-1620
200K    /backup/20261127-1620
-rw-r--r--. 1 root root    331 Nov 27 16:20 SHA256SUMS
-rw-r--r--. 1 root root    112 Nov 27 16:20 attach-sha256.txt
-rw-r--r--. 1 root root 184670 Nov 27 16:20 attach.tar.gz
-rw-r--r--. 1 root root   3565 Nov 27 16:20 boarddb.sql.gz
-rw-r--r--. 1 root root    280 Nov 27 16:20 migration_check.txt
--- 실행 로그 마지막 20줄 ---
```

"실행 로그" 칸이 빈 것은 정상이다. 백업 스크립트는 화면에 출력하지 않고 `logger -t smoke-backup` 으로 시스템 로그에만 남긴다. 실패하면 이 칸에 오류가 붙는다.

## 5. 모니터링 수집 대상 (Prometheus Targets) — 그림 28

```
node   3 / 3 up     (MGMT_HOST:9100 · WEB_HOST:9100 · DATA_HOST:9100)
```
