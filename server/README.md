# Linux 서버·운영 메일

![이준호 · Linux 서버 · 운영 메일](../docs/images/role-server.svg)

**담당자 메일**　[dlwnsgh7789@gmail.com](mailto:dlwnsgh7789@gmail.com)　·　[프로젝트 홈](../README.md)　·　[요구사항](../docs/requirements/README.md)

기존 서버를 정비하고 AWS 이관의 비교 기준이 될 원본 목록과 운영 알림 수신 체계를 준비한다.

| 작업 위치 | 올릴 내용 |
| --- | --- |
| [configuration/](configuration/) | Linux 계정·SSH·로그 및 NFS 구성 |
| [backup/](backup/) | 백업 절차, 게시글 건수와 첨부파일 해시 대조 양식 |
| [mail/](mail/) | Postfix·Roundcube 운영 절차와 알림 수신 결과 |

## 작업 체크리스트

- [ ] [공지 앱 인계표](../app/README.md)에 소스 위치·실행 버전·조회 경로를 적어 강찬영에게 전달한다.
- [ ] 계정·SSH·로그를 정비하고 백업 시각, 원본 게시글 건수·대표 본문·첨부파일 해시를 [백업 폴더](backup/)에 정리한다.
- [ ] 최종 이관 전 쓰기 중지 시점을 맞추고 이우빈과 원본·대상 데이터를 대조한다.
- [ ] 보안 탐지·백업·장애·배포 알림이 운영 메일함에 도착하는지 확인하고 수신 기록을 [메일 폴더](mail/)에 남긴다.

[첫날 작업표와 파트 간 인계](../docs/delivery/README.md#첫날-작업표) · [시연 결과 기록](../docs/delivery/README.md#결과-기록표)

## 팀 연동

이우빈에게 이관 기준 건수와 해시 목록을, 강찬영에게 앱 경로·Java/Tomcat 버전과 공지 검증 경로를 전달한다.
