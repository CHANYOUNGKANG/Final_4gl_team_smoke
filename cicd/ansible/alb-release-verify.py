#!/usr/bin/env python3
"""Read-only preflight for the isolated static Blue/Green fixture."""
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

def main():
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
    check(len(actions) == 1 and actions[0]["Type"] == "forward", "unexpected action")
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
    print("RELEASE VERIFY OK: no mutation; ModifyListener permission not tested", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("RELEASE VERIFY FAILED: " + (str(exc) if isinstance(exc, CheckError) else type(exc).__name__), flush=True)
        sys.exit(1)
