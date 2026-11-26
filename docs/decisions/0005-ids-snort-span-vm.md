# ADR-0005: IDS는 별도 Snort VM과 스위치 SPAN으로 구성한다

- **상태**: 제안
- **날짜**: 2026-11-25
- **담당**: 강민서

## 상황

RFP 요구사항 04는 Kali 모의해킹과 방화벽 설정까지만 정한다. 탐지 장비와 위치는 팀이 정해야 한다. 공격 대상은 본사 서비스망(VLAN 30)이다.

## 검토한 선택지

| 선택지 | 장점 | 단점 |
| --- | --- | --- |
| pfSense 패키지(Snort·Suricata) | VM 추가 없음 | pfSense는 지사 방화벽이라 본사 VLAN 30 트래픽을 못 봄 |
| ASA–스위치 사이 인라인 브리지 | SPAN 미지원 이미지에서도 동작 | 장애 시 서비스 경로 영향 |
| **Core SW-2 SPAN(VLAN 30) → Ubuntu Snort VM** | 원본 통신에 영향 없음, apt 설치 | 스위치 이미지가 SPAN을 지원해야 함 |

## 결정

Snort VM(감시 NIC는 IP 없음, 관리 NIC `10.0.20.20`)을 Core SW-2 SPAN 포트에 붙인다. SPAN이 동작하지 않으면 인라인 브리지로 바꾼다.

## 결과

- 좋아지는 것: 탐지 → swatchdog 메일 → rsyslog 타임라인까지 한 번에 시연.
- 감수하는 것: VM 하나(2 vCPU·4GB) 추가.
- 확인 방법: sqlmap 점검 시 1분 안에 [Snort] 메일, ASA `shun` 후 재공격 실패.
