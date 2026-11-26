#!/usr/bin/env bash
set -euo pipefail
: "${BUILD_COMMIT:?Missing Git SHA}" "${BUILD_NUMBER:?Missing Jenkins build number}"
[[ "$BUILD_COMMIT" =~ ^[a-f0-9]{40}$ && "$BUILD_NUMBER" =~ ^[0-9]+$ ]]
image="notice-ci:${BUILD_COMMIT}-${BUILD_NUMBER}"
name="notice-ci-${BUILD_NUMBER}"
docker build --pull --platform linux/amd64 -f cicd/docker/Dockerfile --build-arg "GIT_COMMIT=$BUILD_COMMIT" -t "$image" .
docker image inspect --format 'image={{.Id}} platform={{.Os}}/{{.Architecture}} user={{.Config.User}}' "$image"
# Isolated H2 only: no real DB settings, no host ports, no operational secrets.
docker run -d --network none --memory 1g --name "$name" \
  -e SPRING_PROFILES_ACTIVE=ci -e APP_SEED=true -e DEPLOY_COLOR=blue \
  -e 'JAVA_OPTS=-Xms128m -Xmx384m' "$image"
trap 'docker rm -fv "$name" >/dev/null 2>&1 || true' EXIT
for attempt in {1..90}; do
  if response=$(timeout 8 docker exec "$name" bash -c 'exec 3<>/dev/tcp/127.0.0.1/8080; printf "GET /health HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n\r\n" >&3; cat <&3' 2>/dev/null) &&
     grep -Eq '^HTTP/1\.[01] 200' <<< "$response" &&
     grep -q '"status":"UP"' <<< "$response" &&
     grep -q '"db":"UP"' <<< "$response" &&
     grep -q '"storage":"UP"' <<< "$response" &&
     grep -q '"color":"blue"' <<< "$response" &&
     grep -q "\"commit\":\"${BUILD_COMMIT:0:7}\"" <<< "$response"; then
    echo "NOTICE DOCKER H2 HEALTH VERIFIED: $image"
    exit 0
  fi
  sleep 2
done
docker logs --tail 100 "$name"
exit 1
