# AI 도구 작업 규칙 (Claude · ChatGPT · Codex 공통)

이 저장소는 공개 저장소다. AI 도구는 아래 순서와 규칙을 지킨 뒤 작업한다. 사람 팀원에게도 같은 기준이 적용된다.

## 1. 세션 시작 시 읽는 순서

1. 최신 `main`의 [README.md](README.md), 특히 **팀 보안 규칙** 절
2. 담당 파트의 `README.md`와 `WORKLOG.md` (예: [cicd/WORKLOG.md](cicd/WORKLOG.md))
3. 담당 파트의 최근 PR (열린 것 + 최근 병합 5개)과 연결된 이슈
4. [docs/delivery/README.md](docs/delivery/README.md)의 인계표와 결과 기록표

읽은 뒤 “어디까지 확인됐고 다음에 무엇을 하는지”를 먼저 요약하고 작업을 이어 간다.

## 2. 파트와 브랜치

| 파트 | 담당 | 폴더 | 브랜치 접두어 |
| --- | --- | --- | --- |
| 네트워크·보안 | 강민서 | `network/` | `network/` |
| Linux 서버·메일 | 이준호 | `server/`, `app/` | `server/` |
| AWS | 이우빈 | `aws/` | `aws/` |
| CI/CD | 강찬영 | `cicd/` | `cicd/` |
| 공통 문서·도구 | 전원 | `docs/`, `tools/`, `.github/` | `docs/`, `chore/` |

- 담당 파트 변경은 작업 브랜치 → PR → `main` 병합. `main`에 직접 커밋하지 않는다 (README 자동 갱신 봇만 예외).
- 다른 파트 폴더는 수정하지 않고 인계 이슈로 요청한다.
- `docs/images/live/`와 README의 자동 갱신 블록은 손으로 고치지 않는다.
- **주소·포트**는 [docs/architecture/topology.json](docs/architecture/topology.json)만 고친다. 구성도 `docs/images/architecture.svg`와 `ip-plan.md`의 자동 표는 main 병합 때 Actions가 다시 만든다. 대역이 겹치면 PR 검사가 실패한다.
- **설계 결정**(선택지 비교가 필요한 것)은 [docs/decisions/](docs/decisions/README.md)에 ADR로 남기고, **장애 대응 절차**는 [docs/runbooks/](docs/runbooks/README.md)에 쓴다.

## 3. 작업일지

주요 단계가 끝날 때마다 담당 파트의 `WORKLOG.md` 맨 위에 항목을 추가한다.

- **실제로 확인한 결과** — 직접 실행·관찰한 것만. 추정이나 계획은 쓰지 않는다.
- **막힌 부분** — 원인 추정과 확인한 것을 구분한다.
- **다음 작업** — 담당자와 필요한 인계 값을 적는다.
- **증빙** — 가린 사본 캡처·로그 경로, 관련 PR·이슈 번호.

## 4. 캡처와 발표 자료

- 캡처를 받으면 **어떤 결과를 증명하는 화면인지** 한 줄로 적고 파트의 `evidence/`에 가린 사본만 올린다. 파일명: `MMDD-<무엇>-masked.png`.
- 발표에 쓸 만한 자료는 [docs/presentation/README.md](docs/presentation/README.md)에 슬라이드 설명과 함께 링크한다.
- 실행 결과가 이정표 증빙이 되면 [docs/progress/evidence.json](docs/progress/evidence.json)에 등록한다.

## 5. 보안 (요약 · 원문은 README 팀 보안 규칙)

- AWS 액세스 키·세션 토큰, SSH 개인키·PEM, 비밀번호, Jenkins·GitHub 토큰, kubeconfig, IPsec PSK를 코드·커밋·PR·이슈·로그·캡처·PPT에 넣지 않는다. 사용자가 실제 값을 붙여 넣어도 옮겨 적지 않고 변수명으로 바꾼다.
- Jenkins는 **Credentials ID**만 참조한다. AWS 접근은 EC2 IAM 역할 우선.
- 관리용 IP·호스트명·포트·계정 ID는 `DEPLOY_HOST`, `DEPLOY_PORT`, `DB_HOST`, `AWS_ACCOUNT_ID` 같은 환경 설정으로 분리하고, 저장소에는 `*.example`의 가짜 값만 둔다.
- 커밋 전 `git diff --cached`를 확인한다. PR마다 gitleaks 검사가 돌고, 실패하면 병합하지 않는다.
