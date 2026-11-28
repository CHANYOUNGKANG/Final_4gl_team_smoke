# 온프레미스 서버 3대 재구축 가이드 (11/26~11/27) · 이준호

이 문서만 보고 같은 환경을 다시 만들 수 있게 정리했다. 실제로 실행해 확인한 결과는 [11/27 확인 기록](../verification/1127-ops-check.md), [11/26 확인 기록](../verification/1126-onprem-service-check.md)에 있고 이 문서는 **순서·명령·설정**을 담는다.

- 공개 저장소라 주소·계정·비밀번호는 변수로 적는다: `MGMT_HOST`·`WEB_HOST`·`DATA_HOST`·`MAIL_RELAY_HOST`·`<DB_PASSWORD>`.
- `[재구성본]` 표시가 있는 설정 파일은 서버 원본 사본이 아니라 확인한 적용값으로 정리한 것이다. 원본 사본은 다음 작업에서 올린다.

## 1. 작업 목적과 사용 기술

| 목적 | 사용 기술 | 이유 |
| --- | --- | --- |
| 서버 한 대에 몰린 역할 분리 | VMware · Rocky Linux 3대 (mgmt·web·data) | 한 곳 장애가 전체 중단으로 번지지 않게, 접근 통제를 단순하게 |
| 3대 설정 통일·재현 | Ansible | 손 설정 누락 방지, 다시 실행해도 같은 결과 |
| 비정상 접근 대응 | sshd 정책 · rsyslog 중앙 로그 | root 대입 차단, 서버가 손상돼도 기록 보존 |
| 디스크 부족 대응 | LVM · NFS | 첨부·DB 공간 분리, 무중단 확장, 첨부 한 곳 보관 |
| 회사 사이트·공지 자료실 | Nginx → Tomcat → MariaDB | 앱 서버 비노출, 웹메일과 같은 주소에서 경로 분리 |
| 데이터 보존 증명 | mysqldump · SHA-256 · `v_migration_check` | 백업·이관 결과를 건수와 해시로 대조 |
| 장애·운영 알림 | Postfix · Dovecot · Roundcube | 백업·문의·장애·배포 알림을 메일함 한 곳으로 |
| 사전 감지 | node_exporter · Prometheus · Grafana | 디스크·메모리가 차오르는 것을 장애 전에 확인 |

## 2. 전체 구성과 서비스 역할

```
사용자 ─▶ web : Nginx(80) ─ /         ─▶ Tomcat(127.0.0.1:8080) 회사 사이트·공지 자료실 (팀 표준 app/)
                         └ /webmail/  ─▶ PHP-FPM ─▶ Roundcube 1.7 ─▶ Dovecot(IMAP)·Postfix(25)
                                         ├─ JDBC 3306 ─▶ data : MariaDB boarddb, roundcubemail
                                         └─ NFS  2049 ─▶ data : /share/attach (LVM 5G)
data : 02:00 smoke-backup-notify.sh ─▶ /backup/YYYYMMDD-HHMM ─▶ [백업] 메일 ─▶ web Postfix ─▶ smoke@
mgmt : Ansible(SSH 키) · rsyslog 514 수신 · 03:00 백업 사본 · Prometheus(9100 수집)·Grafana(3000)
```

| 서버 | 역할 | 주요 서비스·포트 |
| --- | --- | --- |
| mgmt | 관리·로그·백업 사본·모니터링 | sshd 22 · rsyslog 514/tcp · Prometheus 9090 · Grafana 3000 · node_exporter 9100 |
| web | 서비스·메일 | Nginx 80 · Tomcat 8080(로컬만) · Postfix 25 · Dovecot 143 · node_exporter 9100 |
| data | DB·첨부·백업 생성 | MariaDB 3306 · NFS 2049 · node_exporter 9100 |

## 3. 구축 환경과 소프트웨어 버전

| 항목 | 버전·값 | 확인 방법 |
| --- | --- | --- |
| OS | Rocky Linux 10.3 (3대) | `cat /etc/rocky-release` |
| Java · Tomcat | Java 21 · Tomcat 10.1.61 (11/26 설치) | `java -version`, `/opt/tomcat/bin/version.sh` |
| DB | MariaDB 10.11.19 | `mysql -V` |
| 메일 | Dovecot 2.3.21 · Roundcube 1.7.0 · Postfix (Rocky 10 기본 패키지) | `dovecot --version`, `postconf mail_version` |
| 웹 | Nginx · PHP-FPM (Rocky 10 기본 패키지) | `nginx -v`, `php -v` |
| 모니터링 | node_exporter · Prometheus · Grafana (설치 버전은 다음 작업에서 기록) | `node_exporter --version` 등 |
| 가상화·네트워크 | VMware Workstation. 11/27 은 VMware NAT 임시 경로로 3대 통신 (네트워크 장비 경로 미연동) | — |

## 4. 구축 순서

| 순서 | 서버 | 작업 | 설정·스크립트 | 확인 |
| --- | --- | --- | --- | --- |
| 1 | 3대 | OS 설치, 호스트 이름, 시간대 | — | `hostnamectl`, `timedatectl` |
| 2 | mgmt | SSH 키 배포, Ansible 설치, inventory | [ansible/](../configuration/ansible/) | `ansible servers -m ping` |
| 3 | 3대 | 공통 설정 (패키지·chrony·방화벽·hosts) | [common.yml](../configuration/ansible/common.yml) | PLAY RECAP `failed=0` |
| 4 | 3대 | SSH 정책 | [ssh/10-smoke.conf](../configuration/ssh/10-smoke.conf) | `sshd -T`, root 접속 거부 |
| 5 | 3대 | 중앙 로그 | [rsyslog/](../configuration/rsyslog/) | mgmt `/var/log/remote/<호스트>/` |
| 6 | data | LVM·NFS | [data/](../configuration/data/) | `lvs`, `exportfs -v` |
| 7 | web | NFS 마운트 | [web/fstab.example](../configuration/web/fstab.example) | `mount \| grep attach` |
| 8 | data | MariaDB, `boarddb` 스키마, DML 전용 앱 계정 | [app/sql/schema.sql](../../app/sql/schema.sql) | `SHOW GRANTS` |
| 9 | web | Tomcat·Nginx, 팀 표준 앱 ROOT.war | [web/](../configuration/web/) | `/health` UP |
| 10 | data | 이관 기준값 | `v_migration_check` | 건수·해시 |
| 11 | data·mgmt | 백업·사본·복구 시험 | [backup.yml](../configuration/ansible/backup.yml) | `sha256sum -c`, 임시 DB 대조 |
| 12 | web | Postfix·Dovecot·Roundcube | [mail/](../configuration/mail/) | `status=sent`, 웹메일 로그인 |
| 13 | web | 문의 → smoke@ 알림 | `MAIL_TO` | 문의 메일 수신 |
| 14 | data | 백업 결과 메일 래퍼 | [templates/](../configuration/ansible/templates/) | `[백업] data 성공` 수신 |
| 15 | 3대·mgmt | 모니터링 | [monitoring/](../configuration/monitoring/) | Targets 3/3 up |

## 5. 단계별 명령

### 5-1. Ansible (mgmt)

```bash
sudo dnf install -y ansible-core
ssh-keygen -t ed25519                     # 키 생성 (개인키는 mgmt 밖으로 내보내지 않는다)
ssh-copy-id rocky@WEB_HOST; ssh-copy-id rocky@DATA_HOST
cd ~/ansible                              # inventory.ini · ansible.cfg 가 있는 곳에서 실행
ansible servers -m ping
ansible-playbook common.yml --check --diff && ansible-playbook common.yml
```

### 5-2. SSH 정책 (3대)

```bash
ansible-playbook sshd.yml                 # 10-smoke.conf 배포 + sshd 재시작
sudo rm -f /etc/ssh/sshd_config.d/01-permitrootlogin.conf   # 설치 때 생긴 root 허용 파일 (먼저 읽혀 정책을 덮음)
sudo sshd -t && sudo systemctl reload sshd
sudo sshd -T | grep -Ei 'permitrootlogin|allowusers|maxauthtries'
ssh root@WEB_HOST                         # mgmt 에서 시험 → Permission denied 가 정상
```

### 5-3. 중앙 로그 (mgmt 수신, web·data 전송)

```bash
ansible-playbook rsyslog.yml
sudo firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=<서버 대역> port port=514 protocol=tcp accept'   # mgmt
sudo firewall-cmd --reload
logger -t smoke-test "central log test"   # web·data
sudo ls /var/log/remote/ && sudo tail /var/log/remote/web/smoke-test.log   # mgmt
```

### 5-4. LVM·NFS (data → web)

```bash
# data (디스크 이름은 lsblk 로 확인)
sudo pvcreate /dev/<디스크>; sudo vgcreate vg_data /dev/<디스크>
sudo lvcreate -L 5G -n lv_share vg_data; sudo lvcreate -L 4G -n lv_mysql vg_data
sudo mkfs.xfs /dev/vg_data/lv_share; sudo mkfs.xfs /dev/vg_data/lv_mysql
sudo groupadd -g 1500 smokefile; sudo useradd -u 1500 -g 1500 -M -s /sbin/nologin smokefile   # web·data 같은 UID/GID 1500
sudo exportfs -rav                         # /etc/exports: data/exports.example (all_squash, anonuid/anongid=1500)
sudo firewall-cmd --permanent --add-service={nfs,rpc-bind,mountd} && sudo firewall-cmd --reload
# web
showmount -e DATA_HOST
sudo mount -a && mount | grep attach       # fstab: _netdev,nofail
```

### 5-5. DB·앱 (data, web)

```bash
# data
sudo mysql < app/sql/schema.sql            # boarddb, 테이블, v_migration_check
sudo mysql -e "SHOW GRANTS FOR 'boarduser'@'<web 대역>'"   # SELECT·INSERT·UPDATE·DELETE 만 (DDL 권한 회수)
# web
sudo cp ROOT.war /opt/tomcat/webapps/ && sudo systemctl restart tomcat
sudo setsebool -P httpd_can_network_connect 1
sudo nginx -t && sudo systemctl reload nginx
curl -s http://127.0.0.1/health            # {"status":"UP","db":"UP","storage":"UP",...}
```

### 5-6. 백업·복구 (data, mgmt)

```bash
ansible-playbook backup.yml                # smoke-backup.sh · 메일 래퍼 · cron(data 02:00, mgmt 03:00)
sudo /usr/local/bin/smoke-backup-notify.sh; echo rc=$?   # data, 즉시 1회
B=$(ls -1d /backup/2* | tail -1); (cd "$B" && sudo sha256sum -c SHA256SUMS)
sudo mysql -e "CREATE DATABASE boarddb_restore"
zcat "$B/boarddb.sql.gz" | sudo mysql boarddb_restore
# 원본·복원본 v_migration_check 건수·해시 비교 → 같으면 성공
sudo mysql -e "DROP DATABASE boarddb_restore"
ls -l /backup/data/                         # mgmt 03:00 사본
```

### 5-7. 메일 (web)

```bash
sudo dnf install -y postfix dovecot s-nail
sudo postconf -e 'myhostname = mail.smoke.local' 'mydomain = smoke.local' \
  'mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain' \
  'home_mailbox = Maildir/' 'message_size_limit = 20971520' 'inet_interfaces = all'
sudo postconf -e 'mynetworks = 127.0.0.0/8, <사내 서버 대역>'
echo 'auth_username_format = %Ln' | sudo tee -a /etc/dovecot/local.conf
sudo systemctl enable --now postfix dovecot
sudo firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=<사내 서버 대역> service name=smtp accept' && sudo firewall-cmd --reload
sudo useradd -m -s /sbin/nologin smoke && sudo passwd smoke
echo test | mail -s hello user1@smoke.local && sudo tail /var/log/maillog   # status=sent
# Roundcube 1.7: /var/www/roundcube, 설정 DB = data 의 roundcubemail, Nginx /webmail/ → public_html
```

### 5-8. 모니터링 (3대, mgmt)

```bash
ansible-playbook monitoring.yml            # node_exporter 3대 + Prometheus·Grafana(mgmt)
sudo firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=<관리 대역> port port=9100 protocol=tcp accept'
curl -s localhost:9100/metrics | head
# 브라우저: http://MGMT_HOST:9090/targets (3/3 up), http://MGMT_HOST:3000 → 대시보드 1860 가져오기
```

## 6. 검증 명령 요약

| 확인 | 명령 | 기대 결과 | 11/27 결과 |
| --- | --- | --- | --- |
| 3대 연결 | `ansible servers -m ping` | 3대 pong | ✅ |
| SSH 정책 | `sshd -T` | permitrootlogin no · allowusers rocky · maxauthtries 3 | ✅ 3대 동일 |
| root 차단 | `ssh root@WEB_HOST` | Permission denied | ✅ |
| 중앙 로그 | `ls /var/log/remote/` | web · data | ✅ |
| NFS | `mount \| grep attach` | 마운트됨 | ✅ |
| 첨부 해시 | DB `sha256` = `sha256sum` | 일치 | ✅ 1건 |
| 백업 무결성 | `sha256sum -c SHA256SUMS` | 모두 OK | ✅ |
| 복구 | 임시 DB 대조 | 건수·해시 일치 | ✅ |
| 메일 배달 | `/var/log/maillog` | status=sent | ✅ |
| 웹메일 | Roundcube 로그인·송수신 | user1 → user2 | ✅ |
| 문의 알림 | 문의 접수 → smoke@ | 메일 도착 | ✅ |
| 백업 메일 | 래퍼 실행 → smoke@ | `[백업] data 성공` | ✅ rc=0 |
| 모니터링 | Targets | 3/3 up | ✅ |
| 앱 상태 | `curl /health` | UP | ⏳ 팀 표준 앱 재배포 후 재확인 필요 |

## 7. 오류와 해결

| 증상 | 원인 (확인 방법) | 해결 |
| --- | --- | --- |
| root 원격 접속이 계속 허용 | `01-permitrootlogin.conf` 가 먼저 읽힘 (`sshd -T`) | 파일 삭제 후 재확인 |
| Ansible inventory 가 비어 있음 | 홈 폴더에서 실행 | `cd ~/ansible` |
| `templates/...j2` 를 못 찾음 | mgmt 에 템플릿 폴더 없음 | 파일 생성 후 재실행 |
| mgmt rsync 호스트 키 실패 | sudo 실행 시 root known_hosts 사용 | `-o UserKnownHostsFile=/home/rocky/.ssh/known_hosts` |
| sudo 와일드카드 실패 | `*` 확장이 일반 사용자 권한에서 일어남 | `sudo sh -c '...'` |
| `showmount` RPC 오류 | 방화벽에 rpc-bind·mountd 없음 | 서비스 추가 |
| fstab 마운트 실패 | 변수 이름을 그대로 적음 | 실제 값으로 수정 (저장소에는 변수) |
| 재부팅 후 web 부팅 정지 | data 보다 먼저 켜져 NFS 대기 | `_netdev,nofail`, 켜는 순서 data → web → mgmt |
| 502 Bad Gateway | `server.xml` 에 `address` 중복 → Tomcat 기동 실패 | 중복 속성 삭제 |
| `/webmail` 404 | Nginx 블록 없음, Roundcube 1.7 은 `public_html` 기준 | alias·PHP-FPM 블록 작성 |
| Roundcube DB 비밀번호 빈 값 | `read` 프롬프트가 붙여 넣은 줄을 먹음 | vi 로 직접 수정 |
| Roundcube 로그인 실패 | Dovecot 이 `user@domain` 계정을 못 찾음 | `auth_username_format = %Ln` |
| 메일 반송 unknown user | 없는 계정(ops)으로 전달 | smoke 계정 생성, 직접 수신 |
| 다른 서버 메일이 안 옴 (점검 항목) | `inet_interfaces = localhost` 또는 25 차단 | `all`, 사내 대역만 25 허용 |

## 8. 다른 팀원과 연동할 항목

| 대상 | 항목 | 상태 |
| --- | --- | --- |
| 이우빈 | 백업 묶음(덤프·첨부·해시 목록)·기준값 → RDS·S3 복원 후 대조 | 인계 자료 준비 완료, 대조 대기 |
| 이우빈 | SNS 토픽 · SQS 대기열(`RawMessageDelivery=false`) · 온프레미스 수신 전용 최소 권한 | 요청 ([이슈 #29](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/29)) |
| 이우빈·강찬영 | 첨부 저장 방식 (EFS 또는 S3) | 이슈 #11 에서 결정 대기 |
| 강찬영 | 배포 결과·롤백 알림 SNS 발행 (`[배포]` 제목) | PR #23 진행 중 |
| 강찬영 | 팀 표준 앱 계약 (`/health`·검증 API·환경 변수) | PR #21 병합 완료 |

## 9. 미완료와 다음 작업

1. 팀 표준 앱 ROOT.war 재배포 후 `/health` UP 재확인 (11/27 마지막 확인은 Tomcat 재시작 전)
2. Grafana 장애 알림 → smoke@, `/health` 감시
3. 백업 실패 메일 시험, s-nail `-S v15-compat`
4. SQS 수신 스크립트 (AWS 값 수령 후)
5. sshd·rsyslog·monitoring 플레이북 원본과 Nginx 원본을 가린 사본으로 교체
6. 메일함(Maildir) 백업 범위 결정
