![SMOKE. · KDT Final Project · 공지·자료실 인프라 전환](docs/images/team-smoke-cover.svg)

# ㈜스모크 | 공지·자료실 인프라 전환

**온프레미스 보안 인프라 재구축 및 AWS 마이그레이션을 통한 무중단 배포·장애 대응 체계 구축**

KDT 최종 프로젝트　·　스모커 팀 4인　·　2026.11–12　·　프로젝트 설계·구축

[![첫날 작업표](docs/images/nav-start.svg)](docs/delivery/README.md#첫날-작업표) [![작업 이슈 열기](docs/images/nav-task.svg)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.md) [![시연 결과 기록](docs/images/nav-results.svg)](docs/delivery/README.md#결과-기록표)

**팀 구축 진행률**　[최신 팀·파트별 %](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1)　/　[브랜치별 분석 기록](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/workflows/project-progress.yml)　/　[산정 기준과 협업 방식](docs/progress/README.md)

**프로젝트 문서**　 [아키텍처](docs/architecture/README.md)　/　[요구사항 명세서](docs/requirements/README.md)　/　[일정과 검증 계획](docs/delivery/README.md)　/　[수행계획서 원본](docs/originals/project-plan.docx)

## 프로젝트 소개

직원이 공지를 올리고 외부 사용자가 첨부파일을 내려받는 동안, 본사 서버 한 대가 사내 업무와 외부 서비스를 모두 처리한다. 웹 서버에 비정상 접근 흔적이 남아도 로그가 흩어져 경로를 추적하기 어렵고, 새 버전을 배포하려고 Tomcat을 재시작하면 읽던 공지도 끊긴다.

스모커 팀은 **사내망을 접근 목적별로 분리하고, 외부 공지·자료실을 AWS 두 가용 영역으로 이전**한다. 고객이 계속 쓰던 글과 파일을 보존하고, 배포 중에도 같은 주소에서 공지를 읽을 수 있게 하는 것이 목표다.

## 배포 흐름 미리보기

[![ALB가 Blue에서 검증된 Green으로 전환한 뒤, 운영 검사 실패로 Blue에 복귀하는 설계 애니메이션](docs/images/blue-green-flow.gif)](https://smoke-release-lab.chanyoungcplus.chatgpt.site)

**[▶ 브라우저에서 시뮬레이터 열기](https://smoke-release-lab.chanyoungcplus.chatgpt.site)** · [오프라인 버전 다운로드 (.zip)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/raw/refs/heads/main/docs/demo/smoke-demo.zip) · [소스 보기](docs/demo/index.html) · [원본 설계 화면](docs/images/blue-green.png)

시뮬레이터에서 시나리오를 고른다. 인터넷 연결이 없는 발표장에서는 오프라인 버전의 `index.html`을 연다. 발표 때는 **한 단계 진행**으로 멈춰 설명하거나 재생 속도를 바꿀 수 있다. 애니메이션은 배포 설계를 설명한다. 실제 측정값은 [시연 기록표](docs/delivery/README.md#결과-기록표)에 남긴다.

| 선택 | 검사 결과 | 사용자가 접속하는 버전 |
| --- | --- | --- |
| 정상 배포 | Green에서 공지 작성·조회 성공, 전환 후 운영 주소에서도 확인 | Blue → Green |
| 전환 전 검증 실패 | Green 전용 경로에서 공지 조회 실패, Jenkins가 전환 차단 | 처음부터 끝까지 Blue |
| 전환 후 자동 롤백 | 운영 주소에서 오류 감지, 이전 대상 그룹 복귀 후 재검사 | Blue → Green → Blue |

## 구축 진행률

<!-- smoke-progress:start -->
**전체 구축 진행률 0.0%**　·　0/32점

| 파트 | 점수 | 진행률 |
| --- | ---: | ---: |
| 강민서 · 네트워크 | 0/8 | 0.0% |
| 이준호 · 서버 | 0/8 | 0.0% |
| 이우빈 · AWS | 0/8 | 0.0% |
| 강찬영 · CI/CD | 0/8 | 0.0% |
<!-- smoke-progress:end -->

파트마다 이정표 4개를 추적한다. 이정표별로 **구현 근거 1점**, **연결된 실행 결과 1점**을 합산한다. 업무 브랜치를 push하면 Actions 실행 요약에 그 브랜치 점수가 나온다. `main` 점수가 바뀌면 위 표도 자동으로 갱신한다. 이슈 #1에서 어떤 파일이 점수에 반영되었는지 확인할 수 있다.

## 팀 워크스페이스

담당자 카드를 누르면 파트별 체크리스트가 열린다. 공지 웹앱을 넘기거나 빌드할 때는 [공용 앱 폴더](app/)에서 소스와 실행 정보를 확인한다.

| 온프레미스 | AWS · 배포 |
| :---: | :---: |
| [![강민서 · PM · 네트워크 보안](docs/images/role-network.svg)](network/)<br>✉  [ehdanfqnd@naver.com](mailto:ehdanfqnd@naver.com) | [![이우빈 · AWS 클라우드 · 이관](docs/images/role-aws.svg)](aws/)<br>✉  [woobin6318@gmail.com](mailto:woobin6318@gmail.com) |
| [![이준호 · Linux 서버 · 운영 메일](docs/images/role-server.svg)](server/)<br>✉  [dlwnsgh7789@gmail.com](mailto:dlwnsgh7789@gmail.com) | [![강찬영 · CI/CD · 블루그린 배포](docs/images/role-cicd.svg)](cicd/)<br>✉  [chanyoungcplus@gmail.com](mailto:chanyoungcplus@gmail.com) |

## 시스템 아키텍처

[![본사·지사 네트워크, Linux 서버, AWS 이관 경로와 Jenkins 블루그린 배포 파이프라인](docs/images/architecture.png)](docs/architecture/README.md)

| 경로 | 서비스가 동작하는 방식 |
| --- | --- |
| **공지 조회** | HTTPS 요청은 ALB를 거쳐 운영 중인 EKS 버전으로 들어간다. 첨부파일은 CloudFront가 비공개 S3에서 가져와 제공한다. |
| **데이터 이관** | MariaDB 게시글은 RDS로, 첨부파일은 S3로 옮긴다. 전후 게시글 건수·대표 본문·파일 해시를 원본과 대조한다. |
| **배포와 복귀** | Jenkins가 테스트와 WAR 빌드를 실행한다. 커밋 태그를 붙인 Docker 이미지를 ECR에 올린 뒤 Ansible로 Green에 배포하고, 공지 작성·조회에 성공하면 ALB를 전환한다. |
| **운영 알림** | Snort 탐지, 백업 결과, CloudWatch 장애 경보, Jenkins 배포 결과를 운영 메일함에서 확인한다. |

## 기술 스택과 파트 간 인계

| 파트 | 주요 기술 | 다음 파트에 전달할 것 |
| --- | --- | --- |
| 네트워크·보안 | GNS3, Cisco ASA, pfSense, VLAN, IPsec, Snort | 서버망 위치, 허용 경로, 허용·차단 및 탐지 기록 |
| 서버·메일 | Rocky Linux, Nginx, Tomcat, MariaDB, Ansible, Postfix, Roundcube | 앱 소스와 빌드 버전, DB 덤프, 첨부 해시 목록, 운영 메일 수신 기록 |
| AWS 클라우드 | VPC, EKS, ALB, RDS, S3, CloudFront, EFS, Redis, CloudWatch | 후보 검증 경로, 대상 그룹, 전환·복귀 방법, 이관 대조 결과 |
| CI/CD | GitHub Webhook, Jenkins, Maven, Docker, ECR, Ansible, Kubernetes | 커밋별 WAR·이미지 식별자, 정상 전환·롤백 로그, 연속 조회 결과 |

## 요구사항과 인수 기준

### 기능·보안 요구사항

| ID | 요구사항 | 주 담당 / 협업 | 인수 기준 |
| --- | --- | --- | --- |
| SRS-REQ-01 | 본사·지사 VLAN, 라우팅·게이트웨이 이중화, 방화벽 ACL·NAT·IPsec VPN | 강민서 | 업무망의 관리 포트 접근 차단, 관리망 허용, 회선·장비 장애 후 경로 전환과 통신 복구를 기록한다. |
| SRS-REQ-02 | 두 AZ의 EKS, HTTPS ALB와 전환·복귀, RDS·S3 이관 | 이우빈 / 이준호·강찬영 | 버전별 응답, 워커 교체 시간, 이관 전후 건수·해시와 원본 저장소 외부 직접 접근 차단을 확인한다. |
| SRS-REQ-03 | Git 변경으로 테스트·빌드·ECR 등록, 후보 배포·검증·자동 복귀 | 강찬영 / 이우빈 | 커밋·빌드 로그·이미지 태그를 대조하고 배포 중 실패 수와 롤백 후 이전 버전 응답을 확인한다. |
| SRS-REQ-04 | 격리 실습망 보안 점검, 접근 통제와 보안 로그 검증 | 강민서 / 이준호 | 개선 전후 점검 결과와 비인가 접근 차단 기록을 방화벽·IDS 로그와 대조한다. |
| SRS-REQ-05 | 계정·SSH·로그·백업 정비, 원본 목록과 운영 메일 수신 체계 | 이준호 / 강민서·이우빈·강찬영 | 원본 백업과 이관 대조표, Snort·백업·CloudWatch·Jenkins 알림의 메일 수신 기록을 확보한다. |

### 비기능 요구사항

| ID | 항목 | 검증 기준 | 담당 |
| --- | --- | --- | --- |
| NFR-01 | 가용성 | 워커 한 대 중단 중 공지 조회 유지 여부와 ASG의 교체 시간을 측정한다. | 이우빈 |
| NFR-02 | 무중단 배포 | 배포 중 조회 실패 0건을 목표로 삼고 전환 후 검사 실패 시 자동 복귀를 확인한다. | 강찬영 |
| NFR-03 | 데이터 무결성 | 이관 전후 게시글 건수·대표 본문·파일 해시가 모두 일치한 뒤 서비스 주소를 전환한다. | 이준호·이우빈 |
| NFR-04 | 보안 | ACL·보안 그룹·IAM은 최소 권한을 적용하고 관리 접속은 Bastion과 SSH 키 인증을 사용한다. | 강민서·이우빈·이준호 |
| NFR-05 | 성능 | 첨부 다운로드 부하 중 공지 응답을 확인하고 캐시를 거치지 않는 경로를 따로 측정한다. | 이우빈 |
| NFR-06 | 운영성 | 보안·백업·장애·배포 알림을 한 메일함에서 확인하고 운영팀에 대응 절차를 인계한다. | 이준호 |
| NFR-07 | 비용 | 예상 비용과 실제 비용을 비교하고 블루·그린 동시 운영 시간과 워커 용량을 기록한다. | 이우빈·강찬영 |

최종 이관 전에는 글 등록과 파일 업로드를 잠시 멈추고 원본을 대조한다. 건수·본문·해시가 맞으면 주소를 전환한다. [제약사항과 요구사항 원문](docs/requirements/README.md)

## 최종 시연

| 시나리오 | 확인할 결과 |
| --- | --- |
| **원본을 보존했는가?** | 이관 전후 게시글 건수·대표 본문과 첨부파일 SHA-256이 일치한다. |
| **배포 중에도 공지를 읽을 수 있는가?** | 운영 주소를 연속 조회하며 Blue → Green 전환 전후의 응답 버전과 총 요청 수를 기록한다. 목표는 조회 실패 **0건**이다. |
| **새 버전에 오류가 생기면 어떻게 되는가?** | 전환 전 검사에 실패하면 Blue를 유지한다. 전환 후 검사에 실패하면 Blue로 자동 복귀하고 이전 버전이 다시 응답하기까지의 시간을 잰다. |
| **워커 한 대가 멈추면 어떤 영향이 있는가?** | 사용자 요청의 실패·회복 시각과 ASG 대체 워커의 준비 시각을 각각 기록한다. |

[시연 측정값 기록표](docs/delivery/README.md)　·　[고객 시나리오 원본 화면](docs/images/scenario.png)　·　[제공 자료 전체 목록](docs/originals/README.md)

## 팀원이 처음 참여할 때

1. [첫날 작업표](docs/delivery/README.md#첫날-작업표)에서 내 작업과 다음 파트에 넘길 결과를 확인한다.
2. [작업 이슈](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.md)에 요구사항 ID, 담당자, 확인할 결과를 적는다. 다른 파트 값이 필요하면 관련 이슈를 연결한다.
3. 저장소를 복제하고 작업 브랜치를 만든다. 아래는 CI/CD 담당자가 첫 빌드를 준비하는 예다.

```bash
git clone https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke.git
cd Final_4gl_team_smoke
git switch -c cicd/first-war-build
```

4. 구현 파일과 실행 기록을 담당 폴더에 저장한다. PR에 이슈 번호와 검증 결과를 연결하고, 실행 증적은 [진행률 등록 방식](docs/progress/README.md#실행-근거를-올리는-방법)에 맞춰 추가한다.

| 폴더 | 여기에 올릴 것 |
| --- | --- |
| [network/](network/) | 토폴로지, 접근 정책, 통신 검증 기록 |
| [server/](server/) | Linux 설정, 백업, 운영 메일 구성 |
| [aws/](aws/) | 클라우드 인프라, 이관, 장애 측정 |
| [cicd/](cicd/) | Jenkins, Docker, Ansible, Kubernetes, 배포 증적 |
| [app/](app/) | 공지 웹앱 소스와 빌드·실행 인계 정보 |
| [docs/](docs/) | 아키텍처, 요구사항, 일정, 원본 자료와 시뮬레이터 |
| [tools/progress/](tools/progress/) | 파트별 구현·실행 근거 집계 코드 |

**일정**　11월 26일 첫 WAR 빌드 → 12월 5일까지 AWS·배포 연동 → 12월 7일까지 통합 검증 → 12월 9일까지 최종 보고서·발표 자료. [전체 일정과 파트 간 인계표](docs/delivery/README.md)
