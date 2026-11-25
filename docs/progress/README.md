# 팀 구축 진행률

[최신 main 진행률](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/issues/1) · [브랜치별 계산 기록](https://github.com/CHANYOUNGKANG/Final_4gl_team_smoke/actions/workflows/project-progress.yml) · [시연 결과 기록표](../delivery/README.md#결과-기록표)

팀원이 push하면 GitHub Actions가 해당 커밋의 파일을 읽고 실행 요약에 점수와 근거 링크를 표시한다. `main`의 최신 결과는 팀 공용 이슈 #1에 모인다. 업무 브랜치 결과는 그 브랜치 실행 요약에서 본다.

## 무엇을 측정하는가

네트워크·서버·AWS·CI/CD마다 대표 이정표 4개를 골랐다. 파트당 8점, 팀 전체 32점이며 진행률은 획득 점수 ÷ 해당 만점 × 100이다. 요구사항 전체에 대한 검수나 남은 작업 시간과는 별도인 **저장소 기반 구축 지표**다. 설계서·폴더 준비는 이미 마쳤고 별도 점수를 부여하지 않는다.

| 파트 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| 네트워크 | NET1 VLAN·라우팅 | NET2 방화벽 통제 | NET3 지사 VPN | NET4 IDS·로그 |
| Linux 서버 | SRV1 SSH·로그 | SRV2 DB·파일 백업 | SRV3 공지 앱 빌드 기반 | SRV4 운영 메일 |
| AWS | AWS1 EKS·서브넷 | AWS2 HTTPS·전환 | AWS3 데이터 이관 | AWS4 워커·모니터링 |
| CI/CD | CICD1 Jenkins·WAR | CICD2 Docker·ECR | CICD3 후보 배포·상태 검사 | CICD4 전환·롤백 |

- **1점 · 구현 근거** — 담당 폴더의 설정과 스크립트에서 항목별 신호 조합을 찾는다. 예를 들어 CICD2는 Docker 베이스 이미지, 이미지 push, ECR 관련 설정을 함께 찾는다. 콘솔·GNS3에서 직접 구성했거나 코드 형식을 인식하지 못하면 설정 내보내기 또는 캡처를 근거로 등록할 수 있다.
- **추가 1점 · 실행 근거** — 해당 기능을 실행하고 커밋한 로그·측정표·결과 캡처를 연결한다. 코드는 구현 신호로, 이 단계는 팀이 제출한 실행 결과로 표시한다. 자동 집계가 스크린샷의 진위나 운영 환경의 성공을 독립 검증하지는 않는다.
- 코드를 삭제하거나 결과 등록을 제거하면 다음 push에서 다시 계산한다. 구현 근거가 없으면 실행 근거만으로 점수가 올라가지 않는다. 실제 검사는 [요구사항별 인수 기준](../requirements/README.md)을 따른다.

## 실행 근거를 올리는 방법

예를 들어 첫 자동 빌드가 성공하면 Jenkins 콘솔 로그를 `cicd/verification/first-build.log`에 저장한다. [evidence.json](evidence.json)에 아래처럼 **실제 파일 경로와 관찰한 결과**를 입력한 뒤 함께 push한다. 값은 형식 예시다.

```json
{
  "CICD1": {
    "verification": {
      "file": "cicd/verification/first-build.log",
      "observed": "같은 커밋의 Webhook 빌드에서 테스트 통과와 WAR 생성 경로를 확인"
    }
  }
}
```

콘솔 설정 등 구현 근거를 직접 등록할 때는 같은 구조의 `implementation` 키를 쓴다. 개인 키·비밀번호 대신 설정의 필요한 부분과 결과만 공유한다. 자동 분석은 담당 폴더와 공용 앱 폴더, 루트의 일반적인 빌드 파일을 대상으로 한다. 문서의 코드 블록도 분석 대상이므로 예시 설정이 실제 구현처럼 인식되면 근거 파일을 확인한다. 인식 패턴은 [집계 코드](../../tools/progress/report.py)에서 확인할 수 있다.

## 우리 팀에 적용할 GitHub Projects 운영법

| GitHub 권장 방식 | 스모커 팀에서 쓰는 방법 |
| --- | --- |
| 큰 일을 검증 가능한 작은 이슈로 나누기 | ‘블루그린 구축’은 ‘Green에서 공지 작성·조회’, ‘ALB 전환’, ‘자동 복귀 실측’으로 나눈다. 각 이슈에 담당자와 완료 기준을 둔다. |
| 작업의 의존성과 관련 PR 연결하기 | CI/CD 빌드 이슈에는 준호의 앱 인계와 우빈의 EC2 준비 이슈를 연결한다. 구현 PR에 해당 이슈 번호와 확인 결과를 남긴다. |
| 목적별 보기와 기준 문서 공유하기 | 보드를 사용할 때 상태별로 대기·진행·검증·완료를 보고, 일정은 종료일 기준 로드맵으로 본다. 수치의 기준은 공용 진행률 이슈 하나로 통일한다. |
| 반복되는 갱신 자동화하기 | 팀원은 코드·실행 근거를 올리고, 점수와 파일 링크는 매 push에서 다시 계산한다. Projects 보드가 있으면 Auto-add 필터로 새 이슈를 자동 수집할 수 있다. |

[GitHub 공식 모범 사례](https://docs.github.com/ko/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects) · [GitHub Projects 자동 추가](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/adding-items-automatically)
