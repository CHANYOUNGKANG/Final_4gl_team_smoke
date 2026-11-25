![SMOKE. · KDT Final Project · 공지·자료실 인프라 전환](docs/images/team-smoke-cover.svg)

<div align="center">

# ㈜스모크 | 공지·자료실 인프라 전환

**온프레미스 보안 인프라 재구축 및 AWS 마이그레이션을 통한 무중단 배포·장애 대응 체계 구축**

KDT 최종 프로젝트　·　스모커 팀 4인　·　2026.11.21 – 12.09

[![Team progress](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/workflows/project-progress.yml/badge.svg)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/workflows/project-progress.yml)
[![last commit](https://img.shields.io/github/last-commit/CHANYOUNGKANG/Final_4gl_team_smoke?label=%EB%A7%88%EC%A7%80%EB%A7%89%20%EC%BB%A4%EB%B0%8B&color=6b50dc)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commits/main)
[![issues](https://img.shields.io/github/issues/CHANYOUNGKANG/Final_4gl_team_smoke?label=%EC%97%B4%EB%A6%B0%20%EC%9D%B4%EC%8A%88&color=80e4cb)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues)
[![PRs](https://img.shields.io/github/issues-pr/CHANYOUNGKANG/Final_4gl_team_smoke?label=%EC%97%B4%EB%A6%B0%20PR&color=a5b6ff)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/pulls)

[![첫날 작업표](docs/images/nav-start.svg)](docs/delivery/README.md#첫날-작업표) [![작업 이슈 열기](docs/images/nav-task.svg)](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.yml) [![시연 결과 기록](docs/images/nav-results.svg)](docs/delivery/README.md#결과-기록표)

</div>

## 지금 우리 팀

> 아래 두 패널과 활동 표는 **main에 push할 때마다, 그리고 매일 00:05(KST)** GitHub Actions가 다시 그린다. 손으로 고치지 않는다.

[![파트별 구축 진행률](docs/images/live/progress.svg)](docs/progress/README.md)

[![수행계획서 일정과 오늘 위치](docs/images/live/schedule.svg)](docs/delivery/README.md#수행계획서-일정--2026년)

<!-- smoke-activity:start -->
| 최근 커밋 | 작성자 | 시각 (KST) |
| --- | --- | ---: |
| [`628b270`](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/628b270eee0dca78c6609a6ef4cb92c55333e1fd) fix: 최근 활동 시각을 KST 절대 시각으로 표기 | claude | 11/25 21:01 |
| [`b6ea0bf`](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/b6ea0bfb476e25e0840f255a2466935d1f672db4) feat: README 라이브 패널과 팀 작업 공간 구성 | claude | 11/25 20:58 |
| [`390e4a3`](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/390e4a3f416dce45e0901bc316b89dd3fe507ce2) docs: add interactive blue-green demo and evidence-based README scoreb… | CHANYOUNGKANG | 11/25 19:54 |
| [`29e5f96`](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/29e5f96813c736b520fed4e7f4b9172ddd5bca10) feat: push마다 팀 구축 진행률과 항목별 근거 집계 | CHANYOUNGKANG | 11/25 18:49 |
| [`f8ef111`](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/commit/f8ef1119a1f7ea49124aec231c239fa85eef456b) docs: 팀 작업 바로가기, 파트별 실행 순서와 인계표 추가 | CHANYOUNGKANG | 11/25 18:37 |

**열린 이슈·PR**　[#1 팀 구축 진행률 · 구현 근거와 시연 기록](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1)

**작업 브랜치 0개**　아직 없음 · 아래 ‘작업 시작하기’ 참고

<sub>11/25 21:01 KST 기준 · main push와 매일 00:05에 갱신</sub>
<!-- smoke-activity:end -->

<details>
<summary><b>점수표 텍스트로 보기</b> · 산정 기준과 근거 파일</summary>

<!-- smoke-progress:start -->
**전체 구축 진행률 0.0%**　·　0/32점

| 파트 | 점수 | 진행률 |
| --- | ---: | ---: |
| 강민서 · 네트워크 | 0/8 | 0.0% |
| 이준호 · 서버 | 0/8 | 0.0% |
| 이우빈 · AWS | 0/8 | 0.0% |
| 강찬영 · CI/CD | 0/8 | 0.0% |
<!-- smoke-progress:end -->

파트마다 이정표 4개, 이정표별로 **구현 근거 1점 + 실행 근거 1점**. 업무 브랜치를 push하면 Actions 실행 요약에 그 브랜치 점수가 나오고, main 점수는 위 패널과 [이슈 #1](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1)에 모인다. [산정 기준](docs/progress/README.md) · [브랜치별 기록](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/workflows/project-progress.yml)

</details>

## 작업 시작하기

| 순서 | 할 일 | 바로가기 |
| :---: | --- | --- |
| 1 | 오늘 내 작업과 다음 파트에 넘길 결과 확인 | [첫날 작업표](docs/delivery/README.md#첫날-작업표) · [일일 기록](docs/daily/) |
| 2 | 작업 이슈 열기 (파트·요구사항·이정표 선택) | [작업](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=team-task.yml) · [인계 요청](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=handoff.yml) · [막힘·장애](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=blocker.yml) |
| 3 | 브랜치를 만들고 내 파트 폴더에서 작업 | 아래 명령 · [작업 양식](docs/templates/) |
| 4 | PR에 이슈 번호와 확인 결과를 적고 main에 병합 | [PR 체크리스트](.github/PULL_REQUEST_TEMPLATE.md) |
| 5 | 실행 결과를 `evidence.json`에 등록하면 점수 +1 | [등록 방법](docs/progress/README.md#실행-근거를-올리는-방법) · [측정 기록 이슈](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/new?template=demo-result.yml) |

```bash
git clone https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke.git && cd Final_4gl_team_smoke
git switch -c cicd/first-war-build          # <파트>/<작업이름>: network·server·aws·cicd
git add cicd/ && git commit -m "cicd: first WAR build"
git push -u origin cicd/first-war-build     # push하면 Actions가 이 브랜치 점수를 계산
```

**일정**　11/26 첫 WAR 빌드 → 12/5 AWS·배포 연동 → 12/7 통합 검증 → 12/9 최종 보고서·발표. [전체 일정과 인계표](docs/delivery/README.md)

## 팀 워크스페이스

담당자 카드를 누르면 파트별 체크리스트가 열린다. 공지 웹앱을 넘기거나 빌드할 때는 [공용 앱 폴더](app/)의 인계표를 본다.

| 온프레미스 | AWS · 배포 |
| :---: | :---: |
| [![강민서 · PM · 네트워크 보안](docs/images/role-network.svg)](network/)<br>✉  [ehdanfqnd@naver.com](mailto:ehdanfqnd@naver.com) | [![이우빈 · AWS 클라우드 · 이관](docs/images/role-aws.svg)](aws/)<br>✉  [woobin6318@gmail.com](mailto:woobin6318@gmail.com) |
| [![이준호 · Linux 서버 · 운영 메일](docs/images/role-server.svg)](server/)<br>✉  [dlwnsgh7789@gmail.com](mailto:dlwnsgh7789@gmail.com) | [![강찬영 · CI/CD · 블루그린 배포](docs/images/role-cicd.svg)](cicd/)<br>✉  [chanyoungcplus@gmail.com](mailto:chanyoungcplus@gmail.com) |

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

| ID | 요구사항 | 주 담당 / 협업 | 인수 기준 |
| --- | --- | --- | --- |
| SRS-REQ-01 | 본사·지사 VLAN, 라우팅·게이트웨이 이중화, 방화벽 ACL·NAT·IPsec VPN | 강민서 | 업무망의 관리 포트 접근 차단, 관리망 허용, 회선·장비 장애 후 경로 전환과 통신 복구를 기록한다. |
| SRS-REQ-02 | 두 AZ의 EKS, HTTPS ALB와 전환·복귀, RDS·S3 이관 | 이우빈 / 이준호·강찬영 | 버전별 응답, 워커 교체 시간, 이관 전후 건수·해시와 원본 저장소 외부 직접 접근 차단을 확인한다. |
| SRS-REQ-03 | Git 변경으로 테스트·빌드·ECR 등록, 후보 배포·검증·자동 복귀 | 강찬영 / 이우빈 | 커밋·빌드 로그·이미지 태그를 대조하고 배포 중 실패 수와 롤백 후 이전 버전 응답을 확인한다. |
| SRS-REQ-04 | 격리 실습망 보안 점검, 접근 통제와 보안 로그 검증 | 강민서 / 이준호 | 개선 전후 점검 결과와 비인가 접근 차단 기록을 방화벽·IDS 로그와 대조한다. |
| SRS-REQ-05 | 계정·SSH·로그·백업 정비, 원본 목록과 운영 메일 수신 체계 | 이준호 / 강민서·이우빈·강찬영 | 원본 백업과 이관 대조표, Snort·백업·CloudWatch·Jenkins 알림의 메일 수신 기록을 확보한다. |

<details>
<summary><b>비기능 요구사항 NFR-01 – 07</b></summary>

| ID | 항목 | 검증 기준 | 담당 |
| --- | --- | --- | --- |
| NFR-01 | 가용성 | 워커 한 대 중단 중 공지 조회 유지 여부와 ASG의 교체 시간을 측정한다. | 이우빈 |
| NFR-02 | 무중단 배포 | 배포 중 조회 실패 0건을 목표로 삼고 전환 후 검사 실패 시 자동 복귀를 확인한다. | 강찬영 |
| NFR-03 | 데이터 무결성 | 이관 전후 게시글 건수·대표 본문·파일 해시가 모두 일치한 뒤 서비스 주소를 전환한다. | 이준호·이우빈 |
| NFR-04 | 보안 | ACL·보안 그룹·IAM은 최소 권한을 적용하고 관리 접속은 Bastion과 SSH 키 인증을 사용한다. | 강민서·이우빈·이준호 |
| NFR-05 | 성능 | 첨부 다운로드 부하 중 공지 응답을 확인하고 캐시를 거치지 않는 경로를 따로 측정한다. | 이우빈 |
| NFR-06 | 운영성 | 보안·백업·장애·배포 알림을 한 메일함에서 확인하고 운영팀에 대응 절차를 인계한다. | 이준호 |
| NFR-07 | 비용 | 예상 비용과 실제 비용을 비교하고 블루·그린 동시 운영 시간과 워커 용량을 기록한다. | 이우빈·강찬영 |

</details>

최종 이관 전에는 글 등록과 파일 업로드를 잠시 멈추고 원본을 대조한다. 건수·본문·해시가 맞으면 주소를 전환한다. [제약사항과 요구사항 원문](docs/requirements/README.md)

## 최종 시연

| 시나리오 | 확인할 결과 |
| --- | --- |
| **원본을 보존했는가?** | 이관 전후 게시글 건수·대표 본문과 첨부파일 SHA-256이 일치한다. |
| **배포 중에도 공지를 읽을 수 있는가?** | 운영 주소를 연속 조회하며 Blue → Green 전환 전후의 응답 버전과 총 요청 수를 기록한다. 목표는 조회 실패 **0건**이다. |
| **새 버전에 오류가 생기면 어떻게 되는가?** | 전환 전 검사에 실패하면 Blue를 유지한다. 전환 후 검사에 실패하면 Blue로 자동 복귀하고 이전 버전이 다시 응답하기까지의 시간을 잰다. |
| **워커 한 대가 멈추면 어떤 영향이 있는가?** | 사용자 요청의 실패·회복 시각과 ASG 대체 워커의 준비 시각을 각각 기록한다. |

[시연 측정값 기록표](docs/delivery/README.md)　·　[고객 시나리오 원본 화면](docs/images/scenario.png)　·　[제공 자료 전체 목록](docs/originals/README.md)

## 저장소 구조

```text
Final_4gl_team_smoke/
├─ network/        강민서 · topology · policies · verification
├─ server/         이준호 · configuration · backup · mail
├─ aws/            이우빈 · infrastructure · migration · operations
├─ cicd/           강찬영 · jenkins · docker · kubernetes · ansible · verification
├─ app/            공지 웹앱 소스와 인계표
├─ docs/
│  ├─ templates/   파트별 기록 양식·출발점 코드 (점수 집계 제외)
│  ├─ daily/       일일 기록 MMDD.md
│  ├─ delivery/    일정 · 인계 · 결과 기록표
│  ├─ progress/    진행률 기준 · evidence.json
│  ├─ architecture/ requirements/ originals/ demo/
│  └─ images/live/ Actions가 그리는 README 패널
├─ tools/
│  ├─ progress/report.py   이정표 점수 집계
│  └─ readme/build.py      README 라이브 패널 생성
└─ .github/        이슈 폼 4종 · PR 양식 · 라벨 · 워크플로
```
