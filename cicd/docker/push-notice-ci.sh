#!/usr/bin/env bash
set -euo pipefail
: "${SMOKE_AWS_REGION:?Missing AWS region}" "${SMOKE_ECR_REPO:?Missing ECR repo}" "${BUILD_COMMIT:?Missing Git SHA}" "${BUILD_NUMBER:?Missing build number}"
[[ "$BUILD_COMMIT" =~ ^[a-f0-9]{40}$ && "$BUILD_NUMBER" =~ ^[0-9]+$ ]]
tag="notice-${BUILD_COMMIT}-${BUILD_NUMBER}"
uri=$(aws ecr describe-repositories --region "$SMOKE_AWS_REGION" --repository-names "$SMOKE_ECR_REPO" --query 'repositories[0].repositoryUri' --output text)
[[ "$uri" =~ ^[0-9]{12}\.dkr\.ecr\.[a-z0-9-]+\.amazonaws\.com/ ]]
registry="${uri%%/*}"
export DOCKER_CONFIG=$(mktemp -d)
trap 'rm -rf "$DOCKER_CONFIG"' EXIT
aws ecr get-login-password --region "$SMOKE_AWS_REGION" | docker login --username AWS --password-stdin "$registry"
docker tag "notice-ci:${BUILD_COMMIT}-${BUILD_NUMBER}" "$uri:$tag"
docker push "$uri:$tag" > "$DOCKER_CONFIG/push.log"
pushed=$(sed -nE 's/.*digest: (sha256:[a-f0-9]{64}).*/\1/p' "$DOCKER_CONFIG/push.log" | tail -1)
[[ "$pushed" =~ ^sha256:[a-f0-9]{64}$ ]]
remote=$(aws ecr describe-images --region "$SMOKE_AWS_REGION" --repository-name "$SMOKE_ECR_REPO" --image-ids imageTag="$tag" --query 'imageDetails[0].imageDigest' --output text)
[[ "$pushed" == "$remote" ]]
printf 'commit=%s\ntag=%s\ndigest=%s\n' "$BUILD_COMMIT" "$tag" "$remote" | tee app/target/notice-ecr-image.txt
echo "NOTICE ECR PUSH VERIFIED"
