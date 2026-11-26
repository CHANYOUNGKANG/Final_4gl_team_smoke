# 11/26 온프레미스 서버 검증 기록 (이준호)

실제 터미널에서 관찰한 결과만 적는다. 관리 주소는 `MGMT_HOST`·`WEB_HOST`·`DATA_HOST` 로 바꿨다. 화면은 [evidence/2026-11-26](../evidence/2026-11-26/)의 가린 사본.

## 1. Ansible 공통 설정 (mgmt → 3대)

```text
$ ansible-playbook common.yml
PLAY RECAP
data   : ok=6  changed=1  unreachable=0  failed=0  skipped=0  rescued=0  ignored=0
mgmt   : ok=6  changed=1  unreachable=0  failed=0  skipped=0  rescued=0  ignored=0
web    : ok=6  changed=1  unreachable=0  failed=0  skipped=0  rescued=0  ignored=0
```
- changed=1 은 hosts 블록 추가. 시간대·패키지·chronyd·firewalld 는 이미 같은 상태(ok).
- 그림: [1126-11-ansible-common-playbook-masked.png](../evidence/2026-11-26/1126-11-ansible-common-playbook-masked.png)

## 2. data 서버 저장소 (LVM)

```text
$ df -hT | grep -E 'share|mysql'
/dev/mapper/vg_data-lv_share xfs  5.0G  130M  4.9G  3% /share
/dev/mapper/vg_data-lv_db    xfs  4.0G  110M  3.9G  3% /var/lib/mysql
$ lsblk
sda  10G disk  ├─vg_data-lv_share 5G lvm /share  └─vg_data-lv_db 4G lvm /var/lib/mysql
sdb  10G disk  (미사용 · 확장 예비)
nvme0n1 30G disk (OS: /boot 2G, rlm-root 25G, rlm-swap 3G)
```
- 그림: [1126-12-data-lvm-mount-masked.png](../evidence/2026-11-26/1126-12-data-lvm-mount-masked.png)

## 3. MariaDB `smoke_board` 생성

```text
$ sudo mysql -u root -p < smoke_board.sql
category   cnt
공지        2
납품일정    2
도면        2
품질인증    2
notice_count  file_count  content_digest                                                     file_digest
8             0           787ef611bd9c783dca7d17cfbec57f8ec97e1dadf5782403aff2c4fed2217e57   NULL
```
- file_digest NULL = 첨부 0건 상태.
- 그림: [1126-13-mariadb-smoke-board-masked.png](../evidence/2026-11-26/1126-13-mariadb-smoke-board-masked.png)

## 4. web → data NFS 마운트

```text
$ df -h
DATA_HOST:/share/attach  5.0G  129M  4.9G  3%  /var/smoke/attach
```
- 그림: [1126-15-web-nfs-mount-masked.png](../evidence/2026-11-26/1126-15-web-nfs-mount-masked.png)

## 5. web → data DB 접속 (오류 → 해결)

| 시도 | 결과 | 원인 | 조치 |
| --- | --- | --- | --- |
| `mysql -h DATA_HOST -u smoke -p smoke_board` | `ERROR 2002 (HY000) ... (115)` | data firewalld 에 mysql 서비스 없음 | `firewall-cmd --permanent --add-service=mysql` |
| 같은 명령 | `ERROR 1045 (28000) Access denied for user 'smoke'@'WEB_HOST'` | 앱 계정 비밀번호 불일치 (`CREATE USER IF NOT EXISTS` 가 기존 계정을 바꾸지 않음) | `ALTER USER 'smoke'@... IDENTIFIED BY ...` 로 재설정 |
| Tomcat `dbtest.jsp` | `DB FAIL · Socket fail to connect to host:address=(host=DATA_NAT)` | env 파일에 자리표시자 글자가 그대로 들어감 | `/etc/tomcat-smoke.env` 의 `DB_HOST` 수정 후 Tomcat 재시작 |

- 그림: [115](../evidence/2026-11-26/1126-16-trouble-mysql-115-masked.png) · [1045](../evidence/2026-11-26/1126-17-trouble-mysql-1045-masked.png) · [dbtest](../evidence/2026-11-26/1126-18-trouble-dbtest-placeholder-host-masked.png)

## 6. 공지 앱 (Tomcat → MariaDB) 동작

```text
$ curl -s http://localhost:8080/notice/health.jsp
OK notices=8
$ curl -s http://localhost:8080/notice/ | grep -c "view.jsp?id="
8
```
- Tomcat 10.1 에 배포한 [JSP 공지 앱](../onprem-notice-jsp/)이 data 서버 MariaDB 의 `smoke_board` 를 JDBC 로 읽어 목록 8건을 만든다.
- 그림: [1126-19-notice-health-ok-masked.png](../evidence/2026-11-26/1126-19-notice-health-ok-masked.png)

## 아직 확인하지 않은 것

- Nginx(80) → Tomcat 프록시 응답, Tomcat 8080 내부 전용 전환, 방화벽 정리
- 브라우저에서 글쓰기·첨부 업로드·다운로드, 업로드 후 `v_migration_check` 의 file_count·file_digest
- GNS3 경유 VLAN 간 통신 (터널 연결 후 게이트웨이 응답 미확인)
