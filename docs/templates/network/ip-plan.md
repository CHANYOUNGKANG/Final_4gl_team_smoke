# VLAN · IP 계획표

> 확정되면 이준호(서버 위치)·이우빈(이관 출구)과 대조한다.

| VLAN | 이름 | 대역 | 게이트웨이(SVI·HSRP VIP) | 들어가는 장비·서버 |
| ---: | --- | --- | --- | --- |
| 10 | 지사 업무망 |  |  | 지사 PC |
| 20 | 관리망 |  |  | Bastion, 백업, 로그, Snort 관리 NIC |
| 30 | 서비스망 |  |  | Tomcat·Nginx, 메일 서버, DVWA |
| 40 | 서버팜 |  |  | MariaDB, NFS |

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
