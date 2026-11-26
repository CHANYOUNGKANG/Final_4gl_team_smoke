# 네트워크·보안 작업일지

## 2026-11-26 · DAY 1 — GNS3 본사 코어 및 지사 기초 연결

### 실제 확인한 결과
- Core1에서 rapid-PVST, L3 routing, VLAN 10/20/30/40/901 SVI 및 HSRPv2 설정을 적용하고 저장했다.
- VLAN 10~40과 901 SVI up/up 확인. 업무 VLAN 10~40 HSRP Active 확인. VLAN 901 최종 상태는 재확인 필요.
- Core1에서 관리 서버 방향 ICMP 5/5 성공(당일 콘솔 기록 요약).
- pfSense에서 문서용 WAN 인접 라우터로 ICMP 응답 2건 확인. 인터넷 전체 또는 VPN 성공을 의미하지 않는다.
- 설계 화면과 현재 실습 주소 체계 간 차이가 있어 공통 주소표 확정은 보류한다.

### 막힌 부분
- VLAN 20 SVI 주소 중복 로그 반복. VMware VMnet2 호스트 어댑터가 동일 주소를 사용한 화면 확인. 로컬 분리 이후에도 로그가 관찰되어 상대 VMnet 및 중복 L2 경로를 확인해야 한다. 해결 판정 보류.
- IOSv Net Input CPU hog 로그 관찰. 원인은 확정하지 않았다.
- 공통 IP 계획과 실제 실습 대역 불일치: [인계 이슈 #11](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/11). DB 연결 및 VPN/ACL 검증 완료로 표시하지 않는다.

### 다음 작업
- 네트워크 담당: 중복 주소/MAC 경로 확인, HSRP 901 및 Core2 상태 재검증, 절체 시험.
- 서버 담당과 서비스·DB VM 주소/게이트웨이/라우팅 및 MariaDB host 범위 대조 후 공통 IP 계획 확정.
- 본사/지사 통신, 방화벽 허용·차단, VPN, IDS 연동을 순차 검증.

### 증빙
- [DAY1 검증 기록](verification/1126-day1.md)
- [토폴로지 및 주소 대조](topology/1126-day1.md)
- [Core1 설정 요약 및 예시](topology/1126-core1-config.md)
- [pfSense ICMP 응답 캡처](evidence/1126-pfsense-wan-ping-masked.png)

원본 장비 설정, 실제 관리 주소 및 식별자는 공개하지 않는다. 콘솔 기록 요약은 원본 로그 첨부와 구분한다.
