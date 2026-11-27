#!/usr/bin/env python3
"""Read-only dynamic release planner. No patch, modify-listener, or secret access."""
import json
import re
import subprocess
import sys

REGION = "ap-northeast-2"
SLOTS = ("blue", "green")

def require(ok, message):
    if not ok:
        raise ValueError(message)

def select_slots(actions, groups):
    require(set(groups) == set(SLOTS) and len(set(groups.values())) == 2, "invalid target group mapping")
    require(len(actions) == 1 and actions[0].get("Type") == "forward"
            and not actions[0].get("TargetGroupArn"), "expected one weighted forward action")
    fc = actions[0]["ForwardConfig"]
    require(not fc.get("TargetGroupStickinessConfig", {}).get("Enabled", False), "stickiness enabled")
    targets = fc["TargetGroups"]
    require(len(targets) == 2 and {t["TargetGroupArn"] for t in targets} == set(groups.values()),
            "unexpected target groups")
    require(all(type(t.get("Weight")) is int for t in targets), "invalid weights")
    weights = {slot: next(t["Weight"] for t in targets if t["TargetGroupArn"] == groups[slot])
               for slot in SLOTS}
    require(weights in ({"blue": 100, "green": 0}, {"blue": 0, "green": 100}),
            "mixed or unexpected weights; stop")
    active = next(s for s in SLOTS if weights[s] == 100)
    return active, next(s for s in SLOTS if s != active)

def plan_action(active_digest, inactive_digest, candidate_digest):
    if not candidate_digest:
        return "DISCOVER_ONLY"
    if candidate_digest == active_digest:
        return "NOOP_ALREADY_ACTIVE"
    if candidate_digest == inactive_digest:
        return "VERIFY_EXISTING_CANDIDATE"
    return "PLAN_UPDATE_INACTIVE"

def run(argv, label):
    p = subprocess.run(argv, text=True, capture_output=True, timeout=45)
    require(p.returncode == 0, label + " failed (details withheld)")
    return p.stdout

def aws(*args):
    return json.loads(run(["aws", "--region", REGION, "--no-cli-pager", "--output", "json", *args],
                          "AWS " + args[1]))

def kube(*args):
    return json.loads(run(["kubectl", "-n", "notice", "--request-timeout=15s", *args, "-o", "json"],
                          "kubectl " + args[0]))

def get_slot(slot, repo, tg):
    dep = kube("get", "deployment", "notice-" + slot)
    spec, status = dep["spec"], dep["status"]
    labels = {"app": "notice", "slot": slot}
    require(spec["selector"]["matchLabels"] == labels
            and all(spec["template"]["metadata"]["labels"].get(k) == v for k, v in labels.items()),
            slot + " selector mismatch")
    cs = spec["template"]["spec"]["containers"]
    require(len(cs) == 1 and cs[0]["name"] == "notice", slot + " unexpected container")
    image = cs[0]["image"]
    require(re.fullmatch(re.escape(repo) + r"@sha256:[a-f0-9]{64}", image), slot + " image not pinned")
    require(spec["replicas"] == 2 and status.get("readyReplicas") == 2
            and status.get("updatedReplicas") == 2 and status.get("availableReplicas") == 2
            and status.get("observedGeneration") == dep["metadata"]["generation"], slot + " rollout not ready")
    pods = kube("get", "pods", "-l", "app=notice,slot=" + slot)["items"]
    require(len(pods) == 2, slot + " unexpected pod count")
    ips = set()
    for pod in pods:
        md, ps = pod["metadata"], pod["status"]
        require(not md.get("deletionTimestamp") and ps["phase"] == "Running"
                and any(c["type"] == "Ready" and c["status"] == "True" for c in ps.get("conditions", []))
                and len(pod["spec"]["containers"]) == 1
                and pod["spec"]["containers"][0]["image"] == image, slot + " pod not ready or image mismatch")
        ips.add(ps["podIP"])
    health = aws("elbv2", "describe-target-health", "--target-group-arn", tg)["TargetHealthDescriptions"]
    actual = {(t["Target"]["Id"], t["Target"]["Port"]) for t in health if t["TargetHealth"]["State"] == "healthy"}
    require(len(health) == 2 and len(ips) == 2 and actual == {(ip, 8080) for ip in ips},
            slot + " targets not fully healthy/matched (including draining)")
    print("SLOT " + slot + " READY=2 HEALTHY=2 TARGETS_MATCH=2", flush=True)
    return image.split("@", 1)[1]

def main():
    require(len(sys.argv) in (1, 3), "expected no args or candidate account and digest")
    expected_account, candidate = sys.argv[1:] if len(sys.argv) == 3 else ("", "")
    require(not candidate or re.fullmatch(r"sha256:[a-f0-9]{64}", candidate), "bad candidate digest")
    account = aws("sts", "get-caller-identity")["Account"]
    require(re.fullmatch(r"[0-9]{12}", account), "bad account")
    require(not expected_account or expected_account == account, "CI/control host account mismatch")
    ctx = run(["kubectl", "config", "current-context"], "context").strip()
    require(ctx == f"arn:aws:eks:{REGION}:{account}:cluster/smoke-eks", "unexpected context")
    repo = f"{account}.dkr.ecr.{REGION}.amazonaws.com/smoke-notice"
    lbs = aws("elbv2", "describe-load-balancers", "--names", "smoke-alb")["LoadBalancers"]
    require(len(lbs) == 1 and lbs[0]["Type"] == "application" and lbs[0]["State"]["Code"] == "active", "ALB mismatch")
    lb = lbs[0]["LoadBalancerArn"]
    ls = aws("elbv2", "describe-listeners", "--load-balancer-arn", lb)["Listeners"]
    http = [l for l in ls if l["Port"] == 80 and l["Protocol"] == "HTTP"]
    require(len(http) == 1, "HTTP 80 listener not unique")
    listener = http[0]
    rules = aws("elbv2", "describe-rules", "--listener-arn", listener["ListenerArn"])["Rules"]
    require(len(rules) == 1 and rules[0]["IsDefault"], "unexpected listener rules")
    groups = {}
    for slot in SLOTS:
        tgs = aws("elbv2", "describe-target-groups", "--names", "smoke-" + slot + "-tg")["TargetGroups"]
        require(len(tgs) == 1 and tgs[0]["TargetType"] == "ip" and tgs[0]["Port"] == 8080
                and lb in tgs[0]["LoadBalancerArns"], slot + " target group mismatch")
        groups[slot] = tgs[0]["TargetGroupArn"]
    active, inactive = select_slots(listener["DefaultActions"], groups)
    digests = {slot: get_slot(slot, repo, groups[slot]) for slot in SLOTS}
    # Reject routing changes observed during planning; not a transaction or an apply authorization.
    latest = aws("elbv2", "describe-listeners", "--listener-arns", listener["ListenerArn"])["Listeners"]
    require(len(latest) == 1 and select_slots(latest[0]["DefaultActions"], groups) == (active, inactive),
            "routing changed during planning")
    print("ACTIVE_SLOT=" + active + " CANDIDATE_SLOT=" + inactive, flush=True)
    print("NEXT_ACTION=" + plan_action(digests[active], digests[inactive], candidate), flush=True)
    print("NOTICE DYNAMIC PLAN OK: read-only; not authorization to deploy or switch", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("NOTICE DYNAMIC PLAN FAILED: " + (str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else type(exc).__name__), flush=True)
        sys.exit(1)
