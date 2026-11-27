#!/usr/bin/env bash
set -euo pipefail
: "${SMOKE_ANSIBLE_HOST:?Set SMOKE_ANSIBLE_HOST in Jenkins}"
[[ "$SMOKE_ANSIBLE_HOST" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*$ ]]
mode="${CD_MODE:-VERIFY}"
confirm="${CONFIRM_GREEN_OFFLINE:-false}"
digest=""
case "$mode" in
  VERIFY) ;;
  PLAN|DEPLOY)
    : "${SMOKE_AWS_REGION:?Missing region}" "${SMOKE_ECR_REPO:?Missing repo}"
    [[ "$SMOKE_AWS_REGION" == ap-northeast-2 && "$SMOKE_ECR_REPO" == smoke-notice ]]
    [[ "${CANDIDATE_TAG:-}" =~ ^test-[a-f0-9]{40}$ ]]
    digest=$(aws ecr describe-images --region "$SMOKE_AWS_REGION" --repository-name "$SMOKE_ECR_REPO" --image-ids imageTag="$CANDIDATE_TAG" --query 'imageDetails[0].imageDigest' --output text)
    [[ "$digest" =~ ^sha256:[a-f0-9]{64}$ ]]
    echo "CD candidate: tag=$CANDIDATE_TAG digest=$digest"
    ;;
  *) exit 2 ;;
esac
[[ "$confirm" == true || "$confirm" == false ]]
if [[ "$mode" == DEPLOY && "$confirm" != true ]]; then
  echo "Green offline confirmation required" >&2
  exit 2
fi
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes \
  -o ConnectTimeout=10 -i /var/lib/jenkins/.ssh/smoke-deploy \
  "ansadmin@$SMOKE_ANSIBLE_HOST" \
  "set -eu; cd /opt/devops; umask 077; f=\$(mktemp .notice-cd.XXXXXX.yml); trap 'rm -f -- \"\$f\"' EXIT; cat > \"\$f\"; flock -n /opt/devops/.notice-cd.lock ansible-playbook -i localhost, -c local \"\$f\" -e @/opt/devops/bootstrap-smoke.local.yml -e cd_mode=$mode -e candidate_digest=$digest -e green_offline_confirmed=$confirm" \
  < cicd/ansible/notice-cd.yml
