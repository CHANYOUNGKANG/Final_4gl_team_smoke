#!/usr/bin/env python3
"""Guarded release for the isolated static Blue/Green fixture."""
import copy
import os
import signal
from pathlib import Path
import http.client
import json
import re
import subprocess
import sys
import tempfile
import time

REGION = "ap-northeast-2"
DIGEST = {
    "blue": "sha256:89cbb9d7197385f7a77bec308ef85826d86e54180a5c7ffb5aec0af76b290cea",
    "green": "sha256:fe8f3cdccd40fb2c38830118abb3c0ed7d7f2da89ab99c8d3ca77cd3921b03b7",
}
VERSION = {"blue": "test-v2", "green": "test-v4"}

class CheckError(Exception):
    pass

def check(ok, msg):
    if not ok:
        raise CheckError(msg)

def run(args, label):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=40)
        check(p.returncode == 0, label + " failed (private stderr withheld)")
        return p.stdout
    except subprocess.TimeoutExpired:
        raise CheckError(label + " timeout") from None

def aws(*args):
    return json.loads(run(["aws", "--region", REGION, "--no-cli-pager", "--output", "json", *args],
                          "AWS " + args[1]))

def kube(*args):
    return json.loads(run(["kubectl", "-n", "notice", "--request-timeout=15s", *args, "-o", "json"],
                          "kubectl " + args[1]))

def http_ok(host, port, version):
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request("GET", "/", headers={"Connection": "close"})
        response = conn.getresponse()
        body = response.read(65536).decode("utf-8", errors="replace")
        return response.status == 200 and ('<p id="version">' + version + "</p>") in body
    finally:
        conn.close()

def pod_http(name, version):
    with tempfile.TemporaryFile(mode="w+b") as log:
        proc = subprocess.Popen(["kubectl", "-n", "notice", "port-forward", "--address",
                                 "127.0.0.1", "pod/" + name, ":8080"],
                                stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(30):
                log.seek(0)
                match = re.search(rb"Forwarding from 127\.0\.0\.1:(\d+) ->", log.read())
                if match:
                    check(http_ok("127.0.0.1", int(match.group(1)), version), "Pod HTTP/version mismatch")
                    return
                check(proc.poll() is None, "Pod port-forward exited")
                time.sleep(1)
            raise CheckError("Pod port-forward timeout")
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()


def canonical(actions):
    normalized = copy.deepcopy(actions)
    for action in normalized:
        if "ForwardConfig" in action:
            action["ForwardConfig"]["TargetGroups"].sort(key=lambda x: x["TargetGroupArn"])
    return normalized

def read_actions(arn):
    ls = aws("elbv2", "describe-listeners", "--listener-arns", arn)["Listeners"]
    check(len(ls) == 1 and ls[0]["Port"] == 80 and ls[0]["Protocol"] == "HTTP", "listener mismatch")
    return ls[0]["DefaultActions"]

def modify(arn, actions):
    aws("elbv2", "modify-listener", "--listener-arn", arn,
        "--default-actions", json.dumps(actions, separators=(",", ":")))

def confirm_route(arn, expected, host, slot):
    streak = 0
    for attempt in range(1, 16):
        try:
            ok = canonical(read_actions(arn)) == canonical(expected) and http_ok(host, 80, VERSION[slot])
        except (OSError, http.client.HTTPException, CheckError, ValueError, KeyError):
            ok = False
        streak = streak + 1 if ok else 0
        print(f"ALB CHECK attempt={attempt} version={VERSION[slot]} result={'PASS' if ok else 'RETRY'}", flush=True)
        if streak >= 3:
            return
        time.sleep(2)
    raise CheckError("ALB route verification timeout")

def healthy_pair(arn):
    targets = aws("elbv2", "describe-target-health", "--target-group-arn", arn)["TargetHealthDescriptions"]
    return len(targets) == 2 and all(t["TargetHealth"]["State"] == "healthy" for t in targets)

def save_backup(arn, original, changed):
    root = Path("/opt/devops/release-backups")
    root.mkdir(mode=0o700, exist_ok=True)
    check(not root.is_symlink() and root.stat().st_uid == os.getuid()
          and root.stat().st_mode & 0o077 == 0, "backup directory not private")
    fd, name = tempfile.mkstemp(prefix="listener-", suffix=".json", dir=root)
    with os.fdopen(fd, "w") as stream:
        json.dump({"ListenerArn": arn, "DefaultActions": original, "AttemptedActions": changed}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    print("PRIVATE BACKUP SAVED: " + Path(name).name, flush=True)

def release(mode, listener, groups, host):
    arn = listener["ListenerArn"]
    original = copy.deepcopy(listener["DefaultActions"])
    changed = copy.deepcopy(original)
    for target in changed[0]["ForwardConfig"]["TargetGroups"]:
        target["Weight"] = 100 if target["TargetGroupArn"] == groups["green"] else 0
    check(healthy_pair(groups["blue"]) and healthy_pair(groups["green"]), "target health changed")
    check(canonical(read_actions(arn)) == canonical(original), "listener changed concurrently")
    save_backup(arn, original, changed)
    start = time.monotonic()
    injected = False
    try:
        print("ALB SWITCH REQUEST blue=0 green=100", flush=True)
        modify(arn, changed)
        confirm_route(arn, changed, host, "green")
        check(healthy_pair(groups["green"]), "Green target health failed after switch")
        print(f"ALB SWITCH VERIFIED elapsed_s={time.monotonic()-start:.2f}", flush=True)
        if mode == "ROLLBACK_TEST":
            injected = True
            raise CheckError("intentional post-switch assertion failure; no Pod failure injected")
        print("RELEASE SWITCH OK active=green", flush=True)
        return
    except (Exception, KeyboardInterrupt) as exc:
        print("RELEASE CHECK FAILED: " + (str(exc) if isinstance(exc, CheckError) else type(exc).__name__), flush=True)
        rollback_start = time.monotonic()
        try:
            current = read_actions(arn)
            check(canonical(current) in (canonical(original), canonical(changed)),
                  "unexpected concurrent listener change")
            # Restore even when a timed-out write appears not to have changed the route.
            # Do not overwrite unrelated concurrent changes.
            modify(arn, original)
            confirm_route(arn, original, host, "blue")
            check(healthy_pair(groups["blue"]), "Blue target health failed after rollback")
        except (Exception, KeyboardInterrupt):
            raise CheckError("ROLLBACK UNCONFIRMED: stop and contact AWS owner; inspect private backup") from None
        print(f"ROLLBACK VERIFIED blue=100 green=0 elapsed_s={time.monotonic()-rollback_start:.2f}", flush=True)
        if injected:
            print("RELEASE ROLLBACK TEST OK: synthetic assertion failure", flush=True)
            return
        raise CheckError("release failed; original Blue route verified") from None

def interrupted(signum, frame):
    raise CheckError("release interrupted")

def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else "VERIFY"
    check(mode in ("VERIFY", "SWITCH", "ROLLBACK_TEST"), "invalid release mode")
    account = aws("sts", "get-caller-identity")["Account"]
    check(re.fullmatch(r"\d{12}", account), "account mismatch")
    context = run(["kubectl", "config", "current-context"], "context").strip()
    check(context == f"arn:aws:eks:{REGION}:{account}:cluster/smoke-eks", "context mismatch")
    repo = f"{account}.dkr.ecr.{REGION}.amazonaws.com/smoke-notice"
    lbs = aws("elbv2", "describe-load-balancers", "--names", "smoke-alb")["LoadBalancers"]
    check(len(lbs) == 1 and lbs[0]["Type"] == "application" and
          lbs[0]["State"]["Code"] == "active", "ALB not active")
    lb = lbs[0]
    host = lb["DNSName"]
    check(re.fullmatch(r"smoke-alb-[a-zA-Z0-9.-]+\.elb\.amazonaws\.com", host), "ALB DNS mismatch")
    listeners = aws("elbv2", "describe-listeners", "--load-balancer-arn", lb["LoadBalancerArn"])["Listeners"]
    found = [l for l in listeners if l["Port"] == 80 and l["Protocol"] == "HTTP"]
    check(len(found) == 1, "HTTP 80 listener not unique")
    listener = found[0]
    rules = aws("elbv2", "describe-rules", "--listener-arn", listener["ListenerArn"])["Rules"]
    check(len(rules) == 1 and rules[0]["IsDefault"], "non-default rule exists")
    groups = {}
    for slot in ("blue", "green"):
        tgs = aws("elbv2", "describe-target-groups", "--names", "smoke-" + slot + "-tg")["TargetGroups"]
        check(len(tgs) == 1 and tgs[0]["TargetType"] == "ip" and tgs[0]["Port"] == 8080
              and lb["LoadBalancerArn"] in tgs[0]["LoadBalancerArns"], slot + " TG mismatch")
        groups[slot] = tgs[0]["TargetGroupArn"]
    actions = listener["DefaultActions"]
    check(len(actions) == 1 and actions[0]["Type"] == "forward" and not actions[0].get("TargetGroupArn"), "unexpected action")
    fc = actions[0]["ForwardConfig"]
    check(not fc.get("TargetGroupStickinessConfig", {}).get("Enabled", False), "stickiness enabled")
    targets = fc["TargetGroups"]
    check(len(targets) == 2 and {t["TargetGroupArn"] for t in targets} == set(groups.values()), "TG set mismatch")
    weights = {s: next(t["Weight"] for t in targets if t["TargetGroupArn"] == arn)
               for s, arn in groups.items()}
    check(weights == {"blue": 100, "green": 0}, "initial weights changed")
    print("ALB WEIGHTS blue=100 green=0; default rule only", flush=True)
    for slot in ("blue", "green"):
        expected = repo + "@" + DIGEST[slot]
        dep = kube("get", "deployment", "notice-" + slot)
        cs = dep["spec"]["template"]["spec"]["containers"]
        st = dep["status"]
        check(len(cs) == 1 and cs[0]["name"] == "notice" and cs[0]["image"] == expected,
              slot + " deployment digest mismatch")
        check(dep["spec"]["replicas"] == 2 and st.get("readyReplicas") == 2
              and st.get("updatedReplicas") == 2 and st.get("availableReplicas") == 2
              and st.get("observedGeneration") == dep["metadata"]["generation"], slot + " not ready")
        pods = kube("get", "pods", "-l", "app=notice,slot=" + slot)["items"]
        check(len(pods) == 2, slot + " pod count mismatch")
        ips = set()
        for pod in pods:
            md, ps = pod["metadata"], pod["status"]
            check(not md.get("deletionTimestamp") and ps["phase"] == "Running"
                  and any(c["type"] == "Ready" and c["status"] == "True" for c in ps.get("conditions", []))
                  and len(pod["spec"]["containers"]) == 1
                  and pod["spec"]["containers"][0]["image"] == expected, slot + " Pod mismatch")
            ips.add(ps["podIP"])
            pod_http(md["name"], VERSION[slot])
        health = aws("elbv2", "describe-target-health", "--target-group-arn", groups[slot])["TargetHealthDescriptions"]
        check(not any(t["TargetHealth"]["State"] == "draining" for t in health), slot + " old targets still draining")
        actual = {(t["Target"]["Id"], t["Target"]["Port"]) for t in health if t["TargetHealth"]["State"] == "healthy"}
        check(len(health) == 2 and len(ips) == 2 and actual == {(ip, 8080) for ip in ips},
              slot + " healthy target IP mismatch")
        print(f"SLOT {slot} POD_HTTP=200 x2 VERSION={VERSION[slot]} HEALTHY=2 TARGETS_MATCH=2", flush=True)
    for _ in range(3):
        check(http_ok(host, 80, VERSION["blue"]), "ALB baseline HTTP/version mismatch")
    if mode == "VERIFY":
        print("RELEASE VERIFY OK: no mutation; ModifyListener permission not tested", flush=True)
        return
    release(mode, listener, groups, host)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupted)
    try:
        main()
    except Exception as exc:
        print("RELEASE FAILED:  + (str(exc) if isinstance(exc, CheckError) else type(exc).__name__), flush=True)
        sys.exit(1)
