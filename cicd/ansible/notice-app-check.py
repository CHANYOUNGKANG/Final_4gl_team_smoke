#!/usr/bin/env python3
"""Notice application smoke checks through a loopback-only port-forward or test container."""
import argparse
import http.client
import json
import os
import re
import sys
import time
import uuid

class CheckError(Exception):
    pass

def require(ok, msg):
    if not ok:
        raise CheckError(msg)

class Client:
    def __init__(self, port, token):
        require(1 <= port <= 65535, "invalid local port")
        require(len(token) >= 16 and "\r" not in token and "\n" not in token, "missing or invalid check token")
        self.port, self.token = port, token

    def request(self, method, path, expected, body=None, auth=False):
        # No redirects, proxy, external URL, or printing of response bodies/headers.
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=8)
        headers = {"Connection": "close"}
        if auth:
            headers["X-Check-Token"] = self.token
        if body is not None:
            body = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        try:
            conn.request(method, path, body, headers)
            response = conn.getresponse()
            payload = response.read(2 * 1024 * 1024 + 1)
            require(response.status == expected, method + " unexpected HTTP status " + str(response.status))
            require(len(payload) <= 2 * 1024 * 1024, "response too large")
            return payload
        finally:
            conn.close()

def obj(raw):
    value = json.loads(raw)
    require(isinstance(value, dict), "expected JSON object")
    return value

def identity(value, slot, commit, version=None):
    require(value.get("color") == slot and value.get("commit") == commit[:7], "slot/commit mismatch")
    require(isinstance(value.get("version"), str) and bool(value["version"]), "version missing")
    require(version is None or value["version"] == version, "version mismatch")

def read_only(client, slot, commit):
    health = obj(client.request("GET", "/health", 200))
    require(health.get("app") == "haedeun-notice", "unexpected app identity")
    require(all(health.get(k) == "UP" for k in ("status", "db", "storage")), "dependency health not UP")
    identity(health, slot, commit)
    version = obj(client.request("GET", "/version", 200))
    require(version.get("app") == "haedeun-notice", "unexpected app identity")
    identity(version, slot, commit, health["version"])
    client.request("GET", "/notices", 200)
    return health["version"]

def verify(client, slot, commit, write=False):
    version = read_only(client, slot, commit)
    print("NOTICE HEALTH VERSION LIST OK: DB=UP STORAGE=UP slot=" + slot + " commit=" + commit[:7], flush=True)
    if not write:
        return
    marker = "deploy-check-" + uuid.uuid4().hex
    request = {"title": marker, "content": "isolated deployment check " + marker}
    path = "/api/check/notices"
    post_id = None
    confirmed = False
    attempted = False
    try:
        # Without token, the API must reject the exact valid request before authorized creation.
        # Use GET on a nonexistent ID (no mutation) to verify authentication instead of an unauthenticated POST.
        client.request("GET", path + "/2147483647", 401)
        attempted = True
        created = obj(client.request("POST", path, 201, request, auth=True))
        post_id = created.get("id")
        require(type(post_id) is int and 0 < post_id <= 2147483647, "invalid created ID")
        require(created.get("title") == request["title"] and created.get("content") == request["content"], "created content mismatch")
        confirmed = True
        identity(created["servedBy"], slot, commit, version)
        item = path + "/" + str(post_id)
        read = obj(client.request("GET", item, 200, auth=True))
        require(read.get("id") == post_id and read.get("title") == request["title"] and read.get("content") == request["content"], "readback mismatch")
        identity(read["servedBy"], slot, commit, version)
        public = client.request("GET", "/notices", 200)
        require(marker.encode("ascii") not in public, "check notice visible in public list")
        client.request("GET", "/notices/" + str(post_id), 404)
        print("NOTICE CHECK CREATE READ HIDDEN OK", flush=True)
    finally:
        if confirmed:
            # Verify exact ownership before deleting; never blindly delete an arbitrary ID.
            try:
                item = path + "/" + str(post_id)
                own = obj(client.request("GET", item, 200, auth=True))
                require(own.get("id") == post_id and own.get("title") == request["title"] and own.get("content") == request["content"], "cleanup ownership mismatch")
                client.request("DELETE", item, 204, auth=True)
                client.request("GET", item, 404, auth=True)
                print("NOTICE CHECK DELETE VERIFIED: HTTP 204 then 404", flush=True)
            except Exception:
                print("NOTICE CLEANUP UNCONFIRMED: inspect hidden marker " + marker, flush=True)
                raise CheckError("cleanup failed; do not retry blindly") from None
        elif attempted:
            # A timeout/malformed response after POST may mean a row was committed; do not retry POST.
            print("NOTICE CREATE UNCONFIRMED: inspect hidden marker " + marker, flush=True)
    print("NOTICE FUNCTIONAL CHECK OK", flush=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--slot", choices=("blue", "green"), required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--wait", type=int, default=0, choices=range(0, 181), metavar="SECONDS")
    p.add_argument("--write-check", action="store_true", help="explicitly authorize one hidden check row")
    a = p.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", a.commit), "full commit required")
    client = Client(a.port, os.environ.get("CHECK_TOKEN", ""))
    deadline = time.monotonic() + a.wait
    while True:
        try:
            read_only(client, a.slot, a.commit)
            break
        except Exception:
            if time.monotonic() >= deadline:
                raise CheckError("read-only readiness check failed") from None
            time.sleep(2)
    verify(client, a.slot, a.commit, a.write_check)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("NOTICE CHECK FAILED: " + (str(exc) if isinstance(exc, CheckError) else type(exc).__name__), flush=True)
        sys.exit(1)
