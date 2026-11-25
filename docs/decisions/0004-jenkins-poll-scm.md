# ADR-0004: Jenkins 트리거는 Poll SCM을 기본으로 하고 Webhook은 선택으로 둔다

- **상태**: 제안
- **날짜**: 2026-11-25
- **담당**: 강찬영 (보안 그룹: 이우빈)

## 상황

Jenkins EC2는 퍼블릭 서브넷에 있고, 보안 그룹은 8080·22를 **실습 PC 공인 IP/32만** 허용한다([허용표](../architecture/ip-plan.md)). 팀 보안 규칙은 Jenkins 관리 화면의 인터넷 전체 허용을 금지한다. 이 상태에서는 GitHub Webhook 요청이 Jenkins에 도달할 수 없다.

## 검토한 선택지

| 선택지 | 장점 | 단점 |
| --- | --- | --- |
| Webhook + SG에 GitHub hooks 대역 추가 | push 즉시 빌드 | 대역이 바뀔 수 있어 관리 필요, 공개 노출 범위 증가 |
| **Poll SCM (`H/2 * * * *`)** | 들어오는 규칙 추가 없음 | 최대 2분 지연, 2분마다 GitHub 조회 |
| 리버스 프록시·터널 | 즉시 빌드 | 구성 요소 추가, 실습 범위 초과 |

## 결정

[Jenkinsfile](../../cicd/jenkins/Jenkinsfile)에 `pollSCM('H/2 * * * *')`를 기본으로 두고 `githubPush()`도 함께 선언한다. SG에 GitHub hooks 대역을 열기로 하면 코드 변경 없이 즉시 빌드로 바뀐다.

## 결과

- 좋아지는 것: 보안 그룹은 계획 그대로, 공개 저장소라 토큰 없이 체크아웃.
- 감수하는 것: push 후 빌드 시작까지 최대 2분.
- 확인 방법: 테스트 커밋 push → 2분 안에 빌드 시작, 콘솔 SHA = GitHub SHA (CICD1 실행 근거).
