# 실제 공지 앱 운영 연동 준비 (DAY 2 · Draft)

## 범위 및 현재 상태
- 정적 test-v2/v4 CD와 ALB 전환/자동 복귀 검증 완료. 180초 샘플 341/341 성공, 실패 0. 이 결과는 실제 업무 앱의 데이터/세션 검증과 별개.
- 이 PR은 실제 앱 Deployment JSON을 **로컬에서만 생성**하는 초안이다. 클러스터/ALB/DB 수정, Secret 생성, 파이프라인 자동 호출 없음.
- 기존 notice-blue/green Deployment, Service, TargetGroupBinding을 보존한다. 렌더된 Deployment의 이름/selector는 기존 슬롯과 같으므로 무심코 apply하면 실제 리소스가 변경된다. 현재는 apply 금지.
- 첫 실제 앱 배포는 정적 테스트 슬롯에서 업무 앱 슬롯으로 바뀌는 특별한 전환이다. 정적 Blue로 복귀하면 실제 업무 기능은 제공되지 않는다. 두 실제 앱 버전을 확보한 뒤 업무용 롤백으로 평가한다.

## 인계표
| 담당 | 확인할 값 | 상태 |
| --- | --- | --- |
| AWS | RDS 엔드포인트/버전, smoke_board, 3306, 앱 전용 사용자, SG 및 TLS 요구 | 대기 |
| AWS | EFS CSI 및 RWX PVC, POSIX 접근점/UID·GID, 4 Pod 공유 경로 쓰기 검증 | 대기 |
| AWS | S3/CloudFront 역할, 버킷 정책 및 Pod Identity 필요 여부 | 대기 |
| AWS | 실제 앱 ALB health path /health, HTTP→HTTPS 전환 계획, IAM listener 범위 | 대기 |
| AWS/CI | notice namespace Secret 이름/키(DB_PASSWORD, CHECK_TOKEN, ADMIN_PASSWORD), 비밀값은 승인된 경로로만 전달 | 대기 |
| 서버 | 최종 app/ 사용 확정 및 커밋, MariaDB 10.11 스키마, 온프레미스 외부 Tomcat 배포 확인 | 대기 |
| 서버/AWS | 일관된 데이터 덤프/첨부 원본 및 해시, v_migration_check, 이관 정지 시간 및 백업 | 대기 |
| 네트워크 | 이관 통신 경로/ACL 및 최종 검증 | 대기 |

## 렌더링 (로컬 전용; 적용 금지)
1. 현재 공지 앱 이미지는 Java 17/Tomcat 10.1, /health, /version, /notices 및 토큰 기반 검증 API를 사용한다. ECR의 CI 아티팩트 commit/tag/digest를 대조한다. 실제 값은 공개 저장소 밖에 둔다.
2. config/notice-prod.example.json을 비공개 파일로 복사하고 승인된 값을 넣는다. 예시 값은 렌더러에서 거부된다. DB 비밀번호/토큰은 JSON에 넣지 않는다.
3. 렌더러는 JSON 파일만 생성한다. 다음은 승인 및 실제 인계값 확보 후에만 사용하는 예시다.

```bash
umask 077
python3 cicd/kubernetes/render-notice-prod.py --config /opt/devops/notice-prod.local.json --output /opt/devops/notice-prod-rendered.json
```

현재는 서버 dry-run도 미실행. image UID/GID 및 EFS 쓰기 권한이 확인될 때까지 runAsUser/fsGroup 숫자를 임의 지정하지 않았다. Dockerfile의 USER app은 이름이므로 kubelet runAsNonRoot 검증에 숫자 UID가 필요할 수 있다. CI 이미지의 실제 UID/GID를 확인하고 Dockerfile에서 고정하거나 보안 설정을 승인된 숫자로 보완해야 한다. 현재 리소스 requests/limits 및 probe 시간은 초안; 부하/기동 검증 필요. DB 연결 TLS는 AWS 요구사항과 앱 설정을 맞춘 뒤 검증한다.

## 실제 운영 통합 단계
- EFS PVC는 두 슬롯이 동일 경로에 쓰도록 한다. 현재 앱은 파일시스템 구현이므로 S3 직접 사용은 코드 및 테스트 추가 없이는 불가능하다. EFS와 S3의 역할을 확정하기 전 임의 연결 금지.
- 기존 SQL 파일에는 DROP TABLE이 있으므로 이관된 운영 DB에서 재실행 금지. 백업 복원 및 비교 후 DB_DDL=validate, APP_SEED=false.
- 실제 ALB 활성 슬롯을 확인하고, 해당 슬롯은 변경하지 않는다. 최초 후보 배포 전에 /health 대상 검사 정책 및 기존 정적 Blue와의 전환 계획 합의. 필요하면 분리된 실제 앱 환경에서 먼저 검증한다.
- 모든 후보 Pod의 /health(DB/storage UP), /version(color/commit), /notices 검사. 보호된 검증 API로 숨김 글 생성·조회·삭제 및 정리 확인. 토큰/본문 민감값 미출력. 앱 코드 계약 및 반환 형식 확인 후 구현한다.
- 실제 앱 두 버전으로 전환·복귀 반복 시험, 관리자 세션/CSRF 및 첨부 쓰기·다운로드 무결성 확인. 여러 Pod 및 슬롯 간 세션 유지 정책 별도 확정.
- CI → CD → Release 호출은 별도 PR. 승인된 앱 변경만 트리거하고, immutable digest/commit 검증, 활성 슬롯 동적 감지, 공유 잠금, 실패 시 배포 차단 및 운영 복귀를 구현. 현재의 정적 버전 고정 CD/Release 코드를 업무 앱에 직접 재사용하지 않는다.

## DAY 2 추가 인계 및 동적 PLAN (11/27)

AWS 담당자와 논의된 방향: RDS MariaDB 10.11 / smoke_board / 3306, EFS RWX 공용 PVC를 실시간 첨부 저장소로 사용, S3는 온프레미스 첨부 이관 및 객체 저장, CloudFront 다운로드 및 S3 동기화 구현 방식은 추가 협의, Redis 범위는 협의, 도메인/ACM 보류로 HTTP 80 테스트 우선. 구축 완료 정보 및 실제 Secret 값은 아직 인계 전이다. 민감한 사용자/관리자 요청이나 실제 검증 토큰은 외부 HTTP로 전송하지 않는다.

### Dynamic planner (read-only)
- `cicd/ansible/notice-dynamic-plan.py`: 실제 HTTP 80 기본 리스너 가중치, TG 매핑 및 기존 Deployment/Pod/TG 상태 조회. Blue 100/Green 0이면 Green, 반대면 Blue를 후보로 선택한다. 혼합 가중치, stickiness, 예상 외 리스너 규칙, 불일치 또는 draining은 차단. 두 슬롯 모두 현재 Healthy여야 한다.
- `cicd/ansible/test-notice-dynamic-plan.py`: 양방향 슬롯 선택, 잘못된 가중치/대상 그룹/규칙, 중복 이미지 처리의 단위 테스트. 테스트는 AWS 연결 없이 실행된다.
- Jenkins Pipeline Job `smoke-notice-plan`: SCM branch `*/cicd/notice-prod-integration`, script path `cicd/jenkins/Jenkinsfile.notice-plan`, no SCM polling. 첫 실행은 후보 commit/tag/digest 모두 공란. 오프라인 단위 테스트 두 파일을 먼저 실행한 후 기존 Ansible SSH 및 공유 flock으로 읽기 전용 live plan 수행.
- 후보 입력이 있다면 commit/tag/digest 전체를 요구하고 ECR의 실제 digest 및 Jenkins/Ansible AWS 계정을 대조. 활성 이미지와 동일하면 NOOP_ALREADY_ACTIVE, 대기 이미지와 같으면 VERIFY_EXISTING_CANDIDATE, 다르면 PLAN_UPDATE_INACTIVE. 후보 미입력 시 DISCOVER_ONLY.
- 이 검사는 실제 앱 기능 또는 후보 이미지 출처 전체를 증명하지 않으며, 계획 결과는 배포/전환 허가가 아니다. 실제 변경 직전에 다시 검사하고, 잠금을 변경과 복귀까지 유지하는 통합 실행기가 필요하다. 외부 콘솔 변경은 flock으로 차단할 수 없다.
- 현재 CI Jenkinsfile 변경은 이 Draft 브랜치에만 있다. `NOTICE_AUTO_PLAN=true`는 main 병합 및 downstream Job 수동 검증 후에만 설정한다. 기본값 미설정/false. 성공한 ECR 단계의 commit/tag/digest를 읽어 trusted main CI Job에서만 downstream plan 호출, 실패 전파. 두 executor 이상 필요할 수 있으며 Job 대기/timeout도 검증한다. 실제 CD 및 Release mutation 호출은 아직 없음. 기존 smoke-notice-ci/CD/Release Job 설정은 유지한다.
- 실제 업무 앱 배포 후에야 /health 및 /version, 보호된 CRUD, EFS 공유 쓰기, 스키마 호환, ALB 전환 및 롤백을 검증한다. 현재 기존 정적 앱의 실제 배포/전환 결과를 그대로 보존한다. 단위 테스트 및 live plan 실행 증빙은 아직 대기.

## 실제 앱 기능 검증 (DAY 2 추가)

`cicd/ansible/notice-app-check.py`는 loopback TCP 포트만 접속한다. /health의 app/status/db/storage, /version의 version/color/7자리 commit, /notices의 HTTP 200을 검증한다. 명시적 --write-check에서만 고유한 deploy-check UUID 게시글을 POST 201로 생성하고 GET 200 및 본문/servedBy 일치, 공개 목록 숨김 및 공개 상세 404, DELETE 204 및 재조회 404를 확인한다. 토큰 미제공 GET의 401도 검사한다. 토큰은 환경 변수로만 주입하고 응답 본문과 헤더는 로그에 출력하지 않는다. 생성 결과가 불확실한 경우 POST를 자동 재시도하지 않으며, 삭제 전 ID 및 제목/본문 소유권을 검증한다. 정리 실패 시 고유 마커로 수동 확인한다. 실제 데이터 무결성 및 EFS 쓰기/공유 검증은 별도이며 /health의 storage UP은 디렉터리 쓰기 가능 여부 검사이지 실제 파일 입출력 실측이 아니다.

`cicd/ansible/test-notice-app-check.py`는 6개 오프라인 단위 테스트를 제공한다. `cicd/docker/check-notice-local.sh`는 이전 CI의 로컬 이미지 ID와 digest를 비교하고, 랜덤 포트 127.0.0.1 바인딩 및 일회용 검증 토큰으로 폐기 가능한 H2 컨테이너를 실행한다. 이미지 재빌드/Push/Pull을 하지 않는다. 기존 Plan Job에서 RUN_ISOLATED_APP_CHECK=true와 정확한 기존 CI commit/tag/digest를 입력해 실행할 수 있다. 정상 종료 및 일반 오류에서 컨테이너와 익명 볼륨 삭제 시도. 강제 종료나 Docker 오류 시 수동 잔여 리소스 확인 필요. 테스트 이미지가 로컬에 없거나 ID 표현이 다르면 실패하도록 설계했으며 자동 Pull하지 않는다.

권장 시험 입력은 handoff #2에서 확인된 commit acfb0a8e91da202a6fb3859ee955c4ff8bf1e0b5, tag notice-acfb0a8e91da202a6fb3859ee955c4ff8bf1e0b5-2, digest sha256:331728a6bb5f30c8e045d4cdb59a25d8010a9bdc4da44b34f895edeae85705ac. 이전 parent #2/child #3 자동 호출 실측 성공 기록은 verification/1127-notice-handoff-build-2.log 및 1127-notice-plan-build-3-upstream.log. 이번 추가 기능은 코드 작성 단계이며 Jenkins 실측은 아직 대기. 자동 호출 기본값은 RUN_ISOLATED_APP_CHECK=false. 실제 RDS/EFS 연동과 Pod port-forward 검사 및 운영용 롤백 통합은 별도 작업.
