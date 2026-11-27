#!/usr/bin/env python3
"""Render a reviewed candidate Deployment locally. Never contacts or changes AWS/EKS."""
import argparse
import json
import re
from pathlib import Path

def require(ok, message):
    if not ok:
        raise ValueError(message)

def env(name, value):
    return {"name": name, "value": str(value)}

def secret(name, ref):
    return {"name": name, "valueFrom": {"secretKeyRef": {"name": ref, "key": name}}}

def render(c):
    required = {"slot", "image", "commit", "db_host", "db_user", "secret_name", "pvc_name"}
    require(set(c) == required, "Provide exactly the documented non-secret configuration fields")
    slot = c["slot"]
    require(slot in ("blue", "green"), "invalid slot")
    require(re.fullmatch(r"[0-9]{12}\.dkr\.ecr\.ap-northeast-2\.amazonaws\.com/smoke-notice@sha256:[a-f0-9]{64}", c["image"]), "image must be a pinned ECR digest")
    require(not c["image"].startswith("000000000000."), "replace example account")
    require(re.fullmatch(r"[a-f0-9]{40}", c["commit"]), "invalid commit")
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", c["db_host"]) and not c["db_host"].endswith(".invalid"), "replace DB hostname")
    require(re.fullmatch(r"[A-Za-z0-9_]{1,32}", c["db_user"]) and c["db_user"] not in ("root", "admin", "example"), "use dedicated DB user")
    for field in ("secret_name", "pvc_name"):
        require(re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?", c[field]), "invalid " + field)
        require(not c[field].startswith("example-"), "replace " + field)
    require(c["pvc_name"] == "smoke-attachments-pvc", "use the agreed shared EFS PVC")
    labels = {"app": "notice", "slot": slot}
    variables = [env(k, v) for k, v in {
        "SPRING_PROFILES_ACTIVE": "prod", "DB_HOST": c["db_host"],
        "DB_PORT": "3306", "DB_NAME": "boarddb", "DB_USER": c["db_user"],
        "DB_DDL": "validate", "APP_SEED": "false", "APP_STORAGE_DIR": "/var/smoke/attach", "UPLOAD_DIR": "/var/smoke/attach",
        "APP_PORT": "8080", "DEPLOY_COLOR": slot, "GIT_COMMIT": c["commit"],
        "JAVA_OPTS": "-Xms128m -Xmx384m -Djava.security.egd=file:/dev/./urandom",
    }.items()]
    variables += [secret(k, c["secret_name"]) for k in ("DB_PASSWORD", "CHECK_TOKEN", "ADMIN_KEY")]
    def probe(path, period, failures, timeout=3):
        return {"httpGet": {"path": path, "port": "http"}, "periodSeconds": period,
                "failureThreshold": failures, "timeoutSeconds": timeout}
    return {
        "apiVersion": "apps/v1", "kind": "Deployment",
        "metadata": {"name": "notice-" + slot, "namespace": "notice", "labels": labels},
        "spec": {
            "replicas": 2, "revisionHistoryLimit": 3, "progressDeadlineSeconds": 600,
            "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 0}},
            "selector": {"matchLabels": labels},
            "template": {
                "metadata": {"labels": labels},
                "spec": {
                    "automountServiceAccountToken": False,
                    "securityContext": {"runAsNonRoot": True, "runAsUser": 1500, "runAsGroup": 1500,
                                        "seccompProfile": {"type": "RuntimeDefault"}},
                    "terminationGracePeriodSeconds": 45,
                    "nodeSelector": {"kubernetes.io/os": "linux", "kubernetes.io/arch": "amd64"},
                    "topologySpreadConstraints": [{
                        "maxSkew": 1, "topologyKey": "kubernetes.io/hostname",
                        "whenUnsatisfiable": "ScheduleAnyway", "labelSelector": {"matchLabels": labels}
                    }],
                    "containers": [{
                        "name": "notice", "image": c["image"], "imagePullPolicy": "IfNotPresent",
                        "ports": [{"name": "http", "containerPort": 8080}],
                        "env": variables,
                        "securityContext": {"runAsNonRoot": True, "allowPrivilegeEscalation": False,
                                            "capabilities": {"drop": ["ALL"]}},
                        "resources": {"requests": {"cpu": "250m", "memory": "512Mi"},
                                      "limits": {"cpu": "500m", "memory": "1Gi"}},
                        "startupProbe": probe("/health", 5, 60),
                        "readinessProbe": probe("/health", 5, 3),
                        "livenessProbe": {"tcpSocket": {"port": "http"}, "periodSeconds": 10,
                                          "timeoutSeconds": 2, "failureThreshold": 3},
                        "volumeMounts": [{"name": "attachments", "mountPath": "/var/smoke/attach"}]
                    }],
                    "volumes": [{"name": "attachments", "persistentVolumeClaim": {"claimName": c["pvc_name"]}}]
                }
            }
        }
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    data = render(json.loads(a.config.read_text()))
    # Exclusive create, private file. Never overwrite an existing file or print config.
    import os
    fd = os.open(a.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print("NOTICE PROD DRAFT RENDERED: no API calls; not approved for apply")

if __name__ == "__main__":
    main()
