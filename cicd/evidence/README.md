# CI/CD 캡처 · 증빙

민감값을 **가린 사본만** 올린다. 원본(`*-raw.png`)은 `.gitignore`로 제외된다.

## 가리기 전 확인할 곳

| 화면 | 가릴 것 |
| --- | --- |
| Jenkins 콘솔·설정 | 브라우저 주소창(관리 주소), Credentials 값, `initialAdminPassword`, 사용자 이메일 |
| AWS 콘솔 | 우측 상단 계정 ID·사용자명, ARN의 계정 번호, 퍼블릭 IP·DNS |
| 터미널 | 프롬프트의 호스트명·IP, `aws sts get-caller-identity` 결과, 환경 변수 출력 |
| GitHub | Webhook 설정 화면의 Secret, 토큰 화면 |

## 파일 이름

`MMDD-<무엇을 증명>-masked.png` — 예: `1126-cicd1-first-build-success-masked.png`

## 색인

| 파일 | 이 화면이 증명하는 것 | 관련 이정표 · 시험 | 발표 후보 |
| --- | --- | --- | :---: |
| | | | |

발표에 쓸 화면은 [docs/presentation/README.md](../../docs/presentation/README.md) 증빙 색인에도 슬라이드 문구와 함께 추가한다.
