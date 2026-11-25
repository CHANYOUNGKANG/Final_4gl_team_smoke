# 보안 정책

이 저장소는 공개 저장소다. 작업 규칙 원문은 [README의 팀 보안 규칙](README.md#팀-보안-규칙)에 있다.

## 민감값을 발견했거나 올렸을 때

1. **공개 이슈에 원문을 쓰지 않는다.** 팀 채팅으로 해당 계정 담당자에게 바로 알린다. GitHub에서는 Security 탭 → *Report a vulnerability*(비공개 보고)를 쓴다.
2. **먼저 폐기·교체한다.** 커밋을 지우는 것보다 키를 무효화하는 것이 우선이다. Git 이력에서 지워도 이미 복제됐을 수 있다.
   - AWS 키: IAM에서 비활성화 → 삭제 → CloudTrail·비용·리소스 변경 확인
   - SSH 키: 서버 `authorized_keys`에서 공개키 제거 후 새 키 발급
   - GitHub·Jenkins 토큰: 발급 화면에서 폐기 후 재발급, Jenkins Credentials 교체
3. **공개 흔적을 정리한다.** 파일·PR·이슈 댓글·Actions 로그·아티팩트·캡처·PPT를 확인하고 담당자와 이력 정리 여부를 결정한다.

## 자동 검사

| 검사 | 언제 | 실패하면 |
| --- | --- | --- |
| gitleaks (`.github/workflows/secret-scan.yml`) | 모든 push·PR, 매주 월요일 전체 이력 | PR 병합 금지, 위 절차 진행 |
| pre-commit (`.pre-commit-config.yaml`) | 로컬 커밋 직전 (설치한 팀원) | 커밋이 중단됨 |
| GitHub 비밀 스캔·푸시 보호 | 저장소 설정에서 켬 | 푸시 거부 |

로컬 설치: `pip install pre-commit && pre-commit install`
