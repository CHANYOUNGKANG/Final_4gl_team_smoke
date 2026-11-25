# 네트워크 검증 기록 · MMDD

| 시험 | 방법 | 시작 시각 | 결과 시각 | 결과 | 로그 파일 |
| --- | --- | --- | --- | --- | --- |
| HSRP 절체 | R1 인터페이스 shutdown, 지사에서 연속 ping |  |  | 손실 n개 |  |
| ASA Failover | ASA-1 중지 |  |  |  |  |
| VPN 재수립 | 터널 clear 후 재연결 |  |  |  |  |
| 관리망 차단 | 지사 PC → VLAN 20 SSH |  |  | 차단 / 로그 남음 |  |
| IDS 탐지 | Kali sqlmap → DVWA |  |  | [Snort] 메일 수신 |  |

실행 결과를 남겼으면 `docs/progress/evidence.json`의 해당 NET 항목 `verification`에 이 파일을 등록한다.
