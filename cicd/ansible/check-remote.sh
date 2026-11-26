#!/usr/bin/env bash
set -euo pipefail
: "${SMOKE_ANSIBLE_HOST:?Set SMOKE_ANSIBLE_HOST in Jenkins}"
[[ "$SMOKE_ANSIBLE_HOST" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*$ ]]
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes \
  -o ConnectTimeout=10 -i /var/lib/jenkins/.ssh/smoke-deploy \
  "ansadmin@$SMOKE_ANSIBLE_HOST" \
  'set -eu; cd /opt/devops; f=$(mktemp .smoke-check.XXXXXX.yml); trap "rm -f -- \"$f\"" EXIT; cat > "$f"; ansible-playbook -i localhost, -c local "$f"' \
  < cicd/ansible/check-runner.yml
