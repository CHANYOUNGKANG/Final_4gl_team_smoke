#!/usr/bin/env bash
set -euo pipefail
: "${BUILD_COMMIT:?Missing Git commit}" "${BUILD_NUMBER:?Missing Jenkins build number}"
image="smoke-test:${BUILD_COMMIT}"
name="smoke-test-${BUILD_NUMBER}"
docker build --pull --platform linux/amd64 -f cicd/docker/Dockerfile.smoke-test -t "$image" cicd/test-app
docker image inspect --format 'image={{.Id}} platform={{.Os}}/{{.Architecture}}' "$image"
docker run -d --network none --name "$name" "$image"
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
# No host ports are published; test Tomcat through its own loopback.
for attempt in {1..30}; do
  if response=$(timeout 5 docker exec "$name" bash -c 'exec 3<>/dev/tcp/localhost/8080; printf "GET / HTTP/1.0\r\nHost: localhost\r\nConnection: close\r\n\r\n" >&3; cat <&3' 2>/dev/null) &&
     grep -Eq '^HTTP/1\.[01] 200' <<< "$response" &&
     grep -q 'SMOKE CI/CD Test' <<< "$response"; then
    echo "SMOKE HTTP 200: $image"
    exit 0
  fi
  sleep 2
done
docker logs --tail 80 "$name"
exit 1
