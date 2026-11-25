# 허용 · 차단 매트릭스

> 출발 → 도착 한 줄씩. 시연 때 이 표 순서대로 확인하고 결과 열을 채운다. 전체 허용표 원본은 [docs/architecture/ip-plan.md](../../architecture/ip-plan.md#통신-허용표).

| # | 출발 | 도착 | 포트 | 정책 | 적용 장비 · 규칙 이름 | 확인 결과 |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | 지사 PC (VLAN 10) | 공지 웹 (VLAN 30) | TCP 443 | 허용 | pfSense · ASA |  |
| 2 | 지사 PC (VLAN 10) | 관리망 (VLAN 20) | TCP 22 | 차단 | ASA |  |
| 3 | 지사 PC (VLAN 10) | 서버팜 (VLAN 40) | 전체 | 차단 | ASA |  |
| 4 | 관리망 (VLAN 20) | 메일 서버 | TCP 25 | 허용 | ASA |  |
| 5 | NFS 서버 | 인터넷 (S3) | TCP 443 | 허용 | Edge NAT |  |
| 6 | MariaDB 서버 | Bastion 공인 IP | TCP 22 | 허용 | Edge NAT |  |
| 7 | 인터넷 (Kali) | 공지 웹 | 80·443 외 | 차단 | ASA |  |
