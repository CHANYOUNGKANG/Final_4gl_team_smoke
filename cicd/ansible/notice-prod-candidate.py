#!/usr/bin/env python3
"""First real notice candidate deployment. Never changes ALB or active workload."""
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
def load_renderer():
    spec = importlib.util.spec_from_file_location("renderer", ROOT / "kubernetes/render-notice-prod.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def require(ok, msg):
    if not ok:
        raise ValueError(msg)
def run(args, label, timeout=45):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    require(p.returncode == 0, label + " failed; inspect privately")
    return p.stdout
def k(*args, timeout=45):
    return run(["kubectl", "-n", "notice", *args], args[0], timeout)
def deployment(slot):
    return json.loads(k("get", "deployment", "notice-" + slot, "-o", "json"))
def make_patch(old, wanted):
    require(wanted["metadata"]["name"] == "notice-green", "first deployment limited to Green")
    require(old["metadata"]["name"] == "notice-green", "unexpected deployment")
    spec, target = old["spec"], wanted["spec"]
    require(spec["selector"] == target["selector"] and spec["replicas"] == 2, "selector or replicas mismatch")
    require(len(spec["template"]["spec"]["containers"]) == 1 and spec["template"]["spec"]["containers"][0]["name"] == "notice", "unexpected container")
    return [
        {"op": "test", "path": "/metadata/resourceVersion", "value": old["metadata"]["resourceVersion"]},
        {"op": "test", "path": "/spec/selector", "value": spec["selector"]},
        {"op": "test", "path": "/spec/replicas", "value": 2},
        {"op": "replace", "path": "/spec/template", "value": target["template"]},
        {"op": "add", "path": "/spec/strategy", "value": target["strategy"]},
        {"op": "add", "path": "/spec/progressDeadlineSeconds", "value": target["progressDeadlineSeconds"]},
        {"op": "add", "path": "/spec/revisionHistoryLimit", "value": target["revisionHistoryLimit"]},
    ]
def plan(account, digest, expected):
    out = run([sys.executable, str(ROOT / "ansible/notice-dynamic-plan.py"), account, digest], "live plan", 240)
    require("ACTIVE_SLOT=blue CANDIDATE_SLOT=green" in out.splitlines(), "Blue no longer active; stop")
    require("NEXT_ACTION=" + expected in out.splitlines(), "unexpected plan action")
    print(out.strip(), flush=True)
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("DRY_RUN", "DEPLOY"), default="DRY_RUN")
    p.add_argument("--confirm-inactive-green", action="store_true")
    p.add_argument("--commit", required=True)
    p.add_argument("--digest", required=True)
    p.add_argument("--db-host", required=True)
    a = p.parse_args()
    require(a.mode == "DRY_RUN" or a.confirm_inactive_green, "explicit Green approval required")
    require(re.fullmatch(r"[a-f0-9]{40}", a.commit), "invalid commit")
    require(re.fullmatch(r"sha256:[a-f0-9]{64}", a.digest), "invalid digest")
    require(re.fullmatch(r"[a-z0-9.-]+\\.ap-northeast-2\\.rds\\.amazonaws\\.com", a.db_host), "expected private RDS endpoint")
    os.umask(0o077)
    account = run(["aws", "sts", "get-caller-identity", "--query", "Account", "--output", "text"], "identity").strip()
    require(re.fullmatch(r"[0-9]{12}", account), "invalid account")
    require(run(["kubectl", "config", "current-context"], "context").strip() == f"arn:aws:eks:ap-northeast-2:{account}:cluster/smoke-eks", "wrong cluster")
    image = f"{account}.dkr.ecr.ap-northeast-2.amazonaws.com/smoke-notice@{a.digest}"
    wanted = load_renderer().render(dict(slot="green", image=image, commit=a.commit, db_host=a.db_host, db_user="boarduser", secret_name="smoke-notice-secret", pvc_name="smoke-attachments-pvc"))
    with open("/opt/devops/.notice-cd.lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan(account, a.digest, "PLAN_UPDATE_INACTIVE")
        pvc = json.loads(k("get", "pvc", "smoke-attachments-pvc", "-o", "json"))
        require(pvc["status"]["phase"] == "Bound" and "ReadWriteMany" in pvc["spec"]["accessModes"], "PVC not Bound/RWX")
        print("PVC BOUND RWX VERIFIED", flush=True)
        blue = deployment("blue")
        old = deployment("green")
        with tempfile.TemporaryDirectory(prefix="notice-candidate-") as d:
            path = Path(d) / "patch.json"
            path.write_text(json.dumps(make_patch(old, wanted)))
            args = ["patch", "deployment", "notice-green", "--type=json", "--patch-file", str(path)]
            dry = json.loads(k(*args, "--dry-run=server", "-o", "json"))
            require(dry["spec"]["template"]["spec"]["containers"][0]["image"] == image, "dry run image mismatch")
            print("GREEN SERVER DRY RUN OK: no changes", flush=True)
            if a.mode == "DRY_RUN":
                return
            # Recheck listener and both target groups immediately before the patch.
            # The host lock does not prevent independent AWS console/API edits.
            plan(account, a.digest, "PLAN_UPDATE_INACTIVE")
            require(deployment("blue")["spec"] == blue["spec"], "Blue changed")
            require(deployment("green")["metadata"]["resourceVersion"] == old["metadata"]["resourceVersion"], "Green changed; rerun dry run")
            print("GREEN PATCH REQUEST: ALB untouched", flush=True)
            k(*args)
            print("GREEN PATCH APPLIED: candidate remains isolated; no automatic traffic switch", flush=True)
        k("rollout", "status", "deployment/notice-green", "--timeout=600s", timeout=630)
        require(deployment("blue")["spec"] == blue["spec"], "Blue changed during rollout")
        deadline = time.monotonic() + 300
        while True:
            try:
                plan(account, a.digest, "VERIFY_EXISTING_CANDIDATE")
                break
            except ValueError:
                require(time.monotonic() < deadline, "candidate target health not confirmed")
                time.sleep(10)
        print("GREEN CANDIDATE READY: live RDS/EFS and authenticated CRUD still required", flush=True)
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("CANDIDATE STOP: " + (str(e) if isinstance(e, ValueError) else type(e).__name__) + "; inspect state before retrying; no ALB modification requested", file=sys.stderr)
        sys.exit(1)
