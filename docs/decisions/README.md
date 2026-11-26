# 설계 결정 기록 (ADR)

[시스템 아키텍처](../architecture/README.md) · [IP 대역표](../architecture/ip-plan.md) · [양식](adr-template.md)

“왜 이렇게 만들었나”를 결정 하나에 문서 하나로 남긴다. 발표의 **설계 판단** 장과 면접 답변의 근거로 그대로 쓴다. 형식은 [MADR](https://adr.github.io/madr/)을 줄여 썼다.

**쓰는 법**　`adr-template.md`를 `NNNN-짧은-제목.md`로 복사 → 상태 `제안`으로 PR → 관련 담당자가 승인하면 `채택`으로 바꿔 병합. 결정을 뒤집을 때는 기존 문서를 지우지 않고 새 ADR을 만들고 기존 상태를 `대체됨 → ADR-NNNN`으로 바꾼다.

| ADR | 결정 | 상태 | 담당 |
| --- | --- | --- | --- |
| [0001](0001-address-plan-no-overlap.md) | 본사·지사·AWS 대역을 겹치지 않게 나누고 `topology.json` 하나로 관리 | 제안 | 강민서 · 이우빈 |
| [0002](0002-alerts-sns-sqs-pull.md) | 운영 알림은 SNS → SQS에 쌓고 메일 서버가 가져간다 | 제안 | 이준호 · 이우빈 |
| [0003](0003-blue-green-single-eks.md) | 블루그린은 EKS 클러스터 하나 + ALB 대상 그룹 2개 | 제안 | 강찬영 · 이우빈 |
| [0004](0004-jenkins-poll-scm.md) | Jenkins 트리거는 Poll SCM 기본, Webhook은 선택 | 제안 | 강찬영 |
| [0005](0005-ids-snort-span-vm.md) | IDS는 별도 Snort VM + 스위치 SPAN | 제안 | 강민서 |
| [0006](0006-migration-dump-and-sync.md) | 이관은 mysqldump·Bastion·RDS + `aws s3 sync`, 해시로 대조 | 제안 | 이준호 · 이우빈 |
