# 네트워크·보안

![강민서 · PM · 네트워크 보안](../docs/images/role-network.svg)

**담당자 메일**　[ehdanfqnd@naver.com](mailto:ehdanfqnd@naver.com)　·　[프로젝트 홈](../README.md)　·　[요구사항](../docs/requirements/README.md)

본사와 지사 사이의 통신 경로, VLAN별 허용 정책과 장애 시 우회 동작을 관리한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [topology/](topology/) | 본사·지사 연결도와 VLAN·라우팅 표 |
| [policies/](policies/) | 방화벽·VPN 정책과 관리 접속 허용 범위 |
| [verification/](verification/) | 허용·차단 기록, 절체 시간, IDS 로그 대조 결과 |

## 작업 체크리스트

- [ ] [토폴로지](topology/)에 본사·지사 VLAN과 허용 경로를 표시하고 서버 위치를 이준호와 대조한다.
- [ ] 업무망의 공지 조회 허용, 관리 포트 접근 차단, 인가된 관리자 접속을 확인한다.
- [ ] 회선·게이트웨이·방화벽 절체 전후 통신과 복구 시간을 [검증 기록](verification/)에 남긴다.
- [ ] 격리망에서 수집한 IDS·방화벽 기록을 정책과 대조하고 운영 메일 수신을 이준호와 확인한다.

[첫날 작업표와 파트 간 인계](../docs/delivery/README.md#첫날-작업표) · [시연 결과 기록](../docs/delivery/README.md#결과-기록표) · [작업 양식](../docs/templates/README.md) · [작업 이슈 열기](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.yml) · [인계 요청](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=handoff.yml)

## 팀 연동

이준호와 Syslog 수집·메일 수신을 확인하고, 이우빈과 사내 단말의 HTTPS 공지 조회 경로를 검증한다.
