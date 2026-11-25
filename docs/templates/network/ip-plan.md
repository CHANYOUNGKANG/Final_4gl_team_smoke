# VLAN · IP 계획표

> 팀 제안 값은 [docs/architecture/ip-plan.md](../../architecture/ip-plan.md)에 있다. 이 양식은 **GNS3에서 실제로 설정한 값**을 적어 제안 값과 대조할 때 쓴다.

| VLAN | 이름 | 대역 | 게이트웨이(SVI·HSRP VIP) | 들어가는 장비·서버 |
| ---: | --- | --- | --- | --- |
| 10 | 지사 업무망 | 10.1.10.0/24 |  | 지사 PC |
| 20 | 관리망 | 10.0.20.0/24 |  | Bastion, 백업, 로그, Snort 관리 NIC |
| 30 | 서비스망 | 10.0.30.0/24 |  | Tomcat·Nginx, 메일 서버, DVWA |
| 40 | 서버팜 | 10.0.40.0/24 |  | MariaDB, NFS |

## 라우팅 · 이중화

| 구간 | 프로토콜 | 이웃 · AS | 비고 |
| --- | --- | --- | --- |
| Edge R1 ↔ ISP | eBGP |  |  |
| Edge R1 ↔ R2 | iBGP · HSRP |  | Active / Standby |
| 내부 | OSPF |  | area |

## 내보낸 설정 파일

| 장비 | 파일 |
| --- | --- |
| Edge R1 | `network/topology/edge-r1.cfg` |
| ASA-1 | `network/policies/asa-1.cfg` |
