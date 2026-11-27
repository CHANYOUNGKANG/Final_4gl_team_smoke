#!/usr/bin/env bash
# Isolated local CI image, no ECR push/pull, no Kubernetes/ALB/RDS calls.
set +x
set -euo pipefail
: "${CANDIDATE_COMMIT:?}" "${CANDIDATE_TAG:?}" "${CANDIDATE_DIGEST:?}"
[[ "$CANDIDATE_COMMIT" =~ ^[a-f0-9]{40}$ ]]
[[ "$CANDIDATE_TAG" =~ ^notice-$CANDIDATE_COMMIT-[0-9]+$ ]]
[[ "$CANDIDATE_DIGEST" =~ ^sha256:[a-f0-9]{64}$ ]]
local_image="notice-ci:${CANDIDATE_TAG#notice-}"
image_id=$(docker image inspect --format '{{.Id}}' "$local_image")
[[ "$image_id" == "$CANDIDATE_DIGEST" ]] || { echo "Local image ID mismatch; no pull or build attempted"; exit 1; }
echo "LOCAL CI IMAGE ID VERIFIED"
export CHECK_TOKEN
CHECK_TOKEN=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
name="notice-functional-$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
trap 'docker rm -fv "$name" >/dev/null 2>&1 || true; unset CHECK_TOKEN' EXIT
docker run -d --pull=never --name "$name" --memory 1g \
  -p 127.0.0.1::8080 \
  -e CHECK_TOKEN -e SPRING_PROFILES_ACTIVE=ci -e APP_SEED=true \
  -e DEPLOY_COLOR=green -e 'JAVA_OPTS=-Xms128m -Xmx384m' "$image_id" >/dev/null
binding=$(docker port "$name" 8080/tcp)
[[ "$binding" =~ ^127[.]0[.]0[.]1:([0-9]+)$ ]]
port="${BASH_REMATCH[1]}"
python3 cicd/ansible/notice-app-check.py --port "$port" --slot green --commit "$CANDIDATE_COMMIT" --wait 180 --write-check
echo "NOTICE ISOLATED H2 FUNCTIONAL CHECK OK: no production data used"
