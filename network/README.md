# 네트워크·보안

![강민서 · PM · 네트워크 보안](../docs/images/role-network.svg)

**담당자 메일**　[ehdanfqnd@naver.com](mailto:ehdanfqnd@naver.com)　·　[프로젝트 홈](../README.md)　·　[요구사항](../docs/requirements/README.md)

본사와 지사 사이의 통신 경로, VLAN별 허용 정책과 장애 시 우회 동작을 관리한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [topology/](topology/) | 본사·지사 연결도와 VLAN·라우팅 표 |
| [policies/](policies/) | 방화벽·VPN 정책과 관리 접속 허용 범위 |
| [verification/](verification/) | 허용·차단 기록, 절체 시간, IDS 로그 대조 결과 |

## 팀 연동

이준호와 Syslog 수집·메일 수신을 확인하고, 이우빈과 사내 단말의 HTTPS 공지 조회 경로를 검증한다.
