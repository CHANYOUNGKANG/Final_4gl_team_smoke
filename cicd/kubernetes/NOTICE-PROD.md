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
