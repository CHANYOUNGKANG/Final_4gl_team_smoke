# CI/CD 전용 테스트 WAR

실제 공지 앱(app/)이 인계되기 전 Jenkins의 Git 체크아웃, Maven 테스트, WAR 생성, 아티팩트 보관, Poll SCM을 검증하기 위한 임시 앱이다. 실제 서비스 구현·배포 성공이나 CICD1 인수 검증으로 간주하지 않는다.

- Jenkins Script Path: `cicd/jenkins/Jenkinsfile.smoke-test`
- Branch: `*/cicd/chanyoung-day1-first-build`
- Java 21, Maven CLI, JUnit 4 (테스트 전용)
- 결과물: `cicd/test-app/target/smoke-test.war`
- 첫 Build Now 성공 후 index.html의 test-v1을 test-v2로 바꾼 커밋을 push하고 자동 시작 및 SHA 일치를 확인한다.
- 실제 앱 인계 후 기존 `cicd/jenkins/Jenkinsfile`로 전환하고 별도 실제 빌드를 검증한다.
