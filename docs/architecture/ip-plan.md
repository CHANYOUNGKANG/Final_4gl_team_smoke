# IP 대역 · 통신 허용표

[시스템 아키텍처](README.md) · [요구사항](../requirements/README.md) · [팀 보안 규칙](../../README.md#팀-보안-규칙)

<!-- topology-status:start -->
> **상태: 제안 값 · 강민서(GNS3)·이우빈(AWS) 확정 대기 (2026-11-25).** 값을 바꿀 때는 [topology.json](topology.json)만 고쳐 PR을 올린다. 이 문서의 자동 표와 [구성도](../images/architecture.svg)는 main 병합 때 Actions가 다시 만든다.
<!-- topology-status:end -->
> 이 문서는 **GNS3·VMware 실습 주소와 문서용 예약 대역**만 담는다. 실제 PC 공인 IP, AWS 계정 ID, 실제 엔드포인트·호스트명은 적지 않는다 (보안 그룹·Jenkins 전역 변수에만 넣는다).

## 대역 한눈에

<!-- topology-ranges:start -->
| 구역 | 대역 | 용도 |
| --- | --- | --- |
| 본사 사설 | `10.0.0.0/16` | VLAN 10·20·30·40, ASA–스위치 연결 |
| 지사 사설 | `10.1.0.0/16` | 지사 업무망 VLAN 10 |
| GNS3 “공인” 역할 | `198.51.100.0/24` | ISP ↔ 본사·지사, 공지 웹 공인 IP (RFC 5737 문서용 대역) |
| GNS3 인터넷 구간 | `203.0.113.0/24` | ISP 아래 Kali 공격자 (RFC 5737 문서용 대역) |
| AWS VPC | `10.100.0.0/16` | 서울 리전 ap-northeast-2, AZ a·c |
<!-- topology-ranges:end -->

**핵심 규칙**
1. 본사(10.0)·지사(10.1)·AWS(10.100)는 겹치지 않는다. AWS 기본값 `10.0.0.0/16`을 쓰면 본사와 겹친다.
2. `198.51.100.x`·`203.0.113.x`는 GNS3 안에서만 쓰는 “공인 IP 역할” 주소다.
3. GNS3 밖 실제 인터넷으로 나갈 때는 ISP 라우터 NAT ① 때문에 **실습 PC의 실제 공인 IP**로 보인다. AWS 보안 그룹에는 그 값을 `/32`로 넣되, 저장소·캡처·PPT에는 남기지 않는다.

## 네트워크 · GNS3 (강민서)

<!-- topology-gns3:start -->
| 구간 | 대역 | 장비 · 주소 | 메모 |
| --- | --- | --- | --- |
| GNS3 → 실제 인터넷 | `192.168.122.0/24` | ISP g0/0 · DHCP | GNS3 NAT 노드, ISP 라우터 NAT ① (overload) |
| Kali 구간 | `203.0.113.0/24` | ISP `.1` · Kali `.50` | 외부 공격자 위치 |
| ISP ↔ Edge R1 | `198.51.100.0/30` | ISP `.1` · R1 `.2` | eBGP · ISP AS 65100 ↔ 본사 AS 65001 |
| ISP ↔ Edge R2 | `198.51.100.4/30` | ISP `.5` · R2 `.6` | eBGP · R1 ↔ R2 iBGP |
| ISP ↔ 지사 pfSense | `198.51.100.8/30` | ISP `.9` · pfSense WAN `.10` | IPsec VPN 출발지 |
| Edge ↔ ASA (본사 공인) | `198.51.100.128/28` | HSRP `.129` · R1 `.130` · R2 `.131` · ASA outside `.132` (대기 `.133`) | BGP로 ISP에 광고 |
| 공지 웹 Static NAT | — | `198.51.100.140` → `10.0.30.10` | NAT ② · 80/443만. 나머지 내부는 ASA outside `.132`로 PAT |
| ASA ↔ Core SW | `10.0.0.0/29` | ASA inside `.1` · SW-1 `.2` · SW-2 `.3` | 스위치 기본 경로 → `10.0.0.1` |
| ASA Failover | `10.0.255.0/30` | ASA-1 `.1` · ASA-2 `.2` | 상태 동기화 전용 |
| 본사 VLAN 10 업무 | `10.0.10.0/24` | GW `.1` (HSRP) · SW-1 `.2` · SW-2 `.3` | 직원 PC (필요 시) |
| 본사 VLAN 20 관리 | `10.0.20.0/24` | GW `.1` · ① 관리 서버 `.10` · Snort 관리 `.20` | VMnet2 · 실습 PC 어댑터 `.254` |
| 본사 VLAN 30 서비스 | `10.0.30.0/24` | GW `.1` · ② 서비스 서버 `.10` | VMnet3 · DVWA는 같은 VM `:8081` |
| 본사 VLAN 40 서버팜 | `10.0.40.0/24` | GW `.1` · ③ 데이터 서버 `.10` | VMnet4 |
| 지사 VLAN 10 업무 | `10.1.10.0/24` | pfSense LAN `.1` · 지사 PC `.100` | VPN 보호 대역 `10.1.10.0/24 ↔ 10.0.30.0/24` |
<!-- topology-gns3:end -->

### 서버 VM과 서비스 포트 (이준호)

<!-- topology-vms:start -->
| VM | 주소 | 서비스 |
| --- | --- | --- |
| ① 관리 서버 `mgmt` | `10.0.20.10` | SSH Bastion `:22`, Ansible·백업 `/backup`, rsyslog `:514` |
| ② 서비스 서버 `web·mail` | `10.0.30.10` | Tomcat `:8080`, Nginx `:80·443`, 메일 `:25·143`, DVWA `:8081` |
| ③ 데이터 서버 `data` | `10.0.40.10` | MariaDB `:3306`, NFS `:2049`, 원본 해시 목록 |
<!-- topology-vms:end -->

## AWS · VPC (이우빈 · 강찬영)

<!-- topology-aws:start -->
| 서브넷 | AZ a | AZ c | 들어가는 것 | 라우팅 |
| --- | --- | --- | --- | --- |
| 퍼블릭 | `10.100.1.0/24` | `10.100.2.0/24` | ALB · NAT Gateway · Bastion · Jenkins | `0.0.0.0/0` → 인터넷 게이트웨이 |
| 프라이빗 앱 | `10.100.11.0/24` | `10.100.12.0/24` | EKS 워커 · Pod · Ansible EC2 | `0.0.0.0/0` → NAT Gateway |
| 프라이빗 데이터 | `10.100.21.0/24` | `10.100.22.0/24` | RDS 서브넷 그룹 · Redis · EFS 탑재 대상 | 인터넷 경로 없음 |
<!-- topology-aws:end -->

- **EKS**: VPC CNI라 Pod도 프라이빗 앱 서브넷 IP를 받는다. ALB가 서브넷을 찾도록 태그를 단다 — 퍼블릭 `kubernetes.io/role/elb = 1`, 프라이빗 앱 `kubernetes.io/role/internal-elb = 1`.
- **RDS · Route 53**: RDS 서브넷 그룹에 데이터 서브넷 a·c를 넣는다. 앱은 프라이빗 호스팅 영역 `smoke.internal`의 이름(`db.smoke.internal`, `cache.smoke.internal` → 각 엔드포인트 CNAME)으로 붙는다.
- **공개 주소**: 퍼블릭 호스팅 영역에서 `notice.<도메인>` → ALB, `files.<도메인>` → CloudFront (A 별칭), ACM 인증서.

## 통신 허용표

필요한 것만 연다. “어디서 열기”의 모든 지점이 열려야 통신된다.

<!-- topology-allow:start -->
### 본사 안 (VLAN 사이)

| 출발 | 도착 | 포트 | 용도 | 어디서 열기 |
| --- | --- | --- | --- | --- |
| VLAN 20 `10.0.20.10` | 모든 서버 | `22` | SSH · Ansible · rsync 백업 | SW SVI ACL · 각 서버 firewalld |
| VLAN 30 `10.0.30.10` | VLAN 40 `10.0.40.10` | 3306 · 2049 | Tomcat → MariaDB · 첨부 NFS | SW SVI ACL · 데이터 서버 firewalld |
| 모든 서버 · Snort | VLAN 20 `10.0.20.10` | `514` | rsyslog 수집 | SW SVI ACL · 관리 서버 firewalld |
| VLAN 20 · Snort | VLAN 30 메일 `10.0.30.10` | `25` | 백업·탐지 알림 메일 | SW SVI ACL · Postfix `mynetworks` |
| VLAN 30 · 40 | VLAN 20 | 그 외 전부 | 서비스·데이터 → 관리망 선접속 차단 | SW SVI ACL (deny) |

### 본사 밖 ↔ 본사

| 출발 | 도착 | 포트 | 용도 | 어디서 열기 |
| --- | --- | --- | --- | --- |
| 인터넷 · Kali | `198.51.100.140` → `10.0.30.10` | 80 · 443 | 공지 웹 공개 | ASA outside ACL + Static NAT |
| 지사 PC `10.1.10.0/24` | VLAN 30 `10.0.30.10` | 80 · 443 | 공지 웹 · 웹메일만 | pfSense · IPsec · ASA ACL (VLAN 20·40 차단) |
| 본사 서버 전체 | 인터넷 | 80 · 443 · 53 | dnf · aws cli · DNS | ASA PAT `.132` → R1/R2 → ISP NAT ① |

### 본사 ↔ AWS (인터넷 경유)

| 출발 | 도착 | 포트 | 용도 | 어디서 열기 |
| --- | --- | --- | --- | --- |
| 관리 서버 `10.0.20.10` | Bastion 공인 IP | `22` | mysqldump 파일 scp | Bastion SG: 22 ← 실습 PC 공인 IP/32 |
| 데이터 서버 `10.0.40.10` | S3 | `443` | `aws s3 sync` 첨부 | ASA 아웃바운드 443 · IAM 정책 |
| 메일 서버 `10.0.30.10` | SQS | `443` | CloudWatch·Jenkins 알림 수신 | ASA 아웃바운드 443 · IAM 정책 |

### AWS 안 (보안 그룹 참조)

| 출발 | 도착 | 포트 | 용도 | 어디서 열기 |
| --- | --- | --- | --- | --- |
| 인터넷 | ALB SG | 443 (80 → 443 리다이렉트) | 공지 사이트 | ALB SG: `0.0.0.0/0` |
| ALB SG | 워커 노드 SG | 8080 (Pod) | 대상 그룹 → Tomcat Pod | 노드 SG: 소스 = ALB SG |
| 워커 노드 SG | RDS · Redis · EFS SG | 3306 · 6379 · 2049 | 앱 → 데이터 | 각 SG: 소스 = 노드 SG |
| Bastion SG | RDS SG | `3306` | 덤프 복원 | RDS SG: 소스 = Bastion SG |
| 실습 PC 공인 IP | Jenkins SG | 8080 · 22 | Jenkins 화면 · 관리 | Jenkins SG: `<실습 PC 공인 IP>/32` |
| Jenkins · Ansible | EKS API · ECR | `443` | 배포 · 이미지 푸시 | IAM 역할 · EKS Access Entry |
<!-- topology-allow:end -->

## 확인 순서 (구축 첫날)

1. **본사 안**: 서버에서 게이트웨이 → 다른 VLAN 서버 순서. 허용표에 없는 포트는 막혀야 정상.
2. **인터넷 · 지사**: 서버에서 밖으로, Kali에서 공지 웹으로. 실습 PC 공인 IP는 이때 확인해 이우빈에게 **팀 채팅으로** 전달한다.
3. **AWS**: Bastion SG에 그 IP를 넣고 관리 서버에서 접속 → 서버에서 S3·SQS까지 되면 이관·알림 경로 완성.

```bash
ping -c 3 10.0.20.1
ping -c 3 10.0.40.10
nc -zv 10.0.40.10 3306
nc -zv 10.0.20.10 22
ping -c 3 8.8.8.8
curl -I http://198.51.100.140
```

`nc -zv 10.0.20.10 22`는 서비스 서버에서 실행해 **막히는 것**이 정상이다.

## 대시보드와 다른 점 · 확인 필요

| 항목 | 내용 | 확인할 사람 |
| --- | --- | --- |
| DVWA 포트 | 표는 `:8081`, 모의해킹 절차 예시는 `docker run -p 8080:80`. Tomcat이 8080을 쓰므로 DVWA는 `-p 8081:80`으로 맞춰야 한다. | 강민서 · 이준호 |
| NAT ② 설명 | 구성도 툴팁에 “내부 10.10.x.x”로 남아 있다. 실제 계획은 `10.0.x.x`. | 대시보드 작성자 |
| Jenkins 트리거 | 계획은 Jenkins SG를 실습 PC IP/32로만 연다 → GitHub Webhook이 들어올 수 없다. **Poll SCM**을 기본으로 한다 ([ADR-0004](../decisions/0004-jenkins-poll-scm.md)). | 강찬영 · 이우빈 |

## 변경 기록

| 날짜 | 변경 | 출처 |
| --- | --- | --- |
| 2026-11-25 | 최초 반영 (제안 값) | 팀 아키텍처 대시보드 IP 대역 · 통신 허용표 |
| 2026-11-25 | 표를 [topology.json](topology.json) 자동 생성으로 전환 | 단일 기준 파일 |
