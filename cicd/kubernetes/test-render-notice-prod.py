#!/usr/bin/env python3
"""Offline tests, no AWS or Kubernetes access."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("renderer", Path(__file__).with_name("render-notice-prod.py"))
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

class RendererTests(unittest.TestCase):
    def config(self):
        return dict(slot="green",
                    image="111111111111.dkr.ecr.ap-northeast-2.amazonaws.com/smoke-notice@sha256:"+"a"*64,
                    commit="b"*40, db_host="db.test.example", db_user="notice_app",
                    secret_name="notice-runtime", pvc_name="smoke-attachments-pvc")

    def test_candidate_contract(self):
        d = renderer.render(self.config())
        self.assertEqual(d["metadata"]["namespace"], "notice")
        self.assertEqual(d["metadata"]["name"], "notice-green")
        spec = d["spec"]
        self.assertEqual(spec["replicas"], 2)
        self.assertEqual(spec["selector"]["matchLabels"], spec["template"]["metadata"]["labels"])
        pod = spec["template"]["spec"]
        c = pod["containers"][0]
        values = {e["name"]: e for e in c["env"]}
        self.assertEqual(values["SPRING_PROFILES_ACTIVE"]["value"], "prod")
        self.assertEqual(values["APP_SEED"]["value"], "false")
        self.assertEqual(values["DB_DDL"]["value"], "validate")
        self.assertEqual(values["DEPLOY_COLOR"]["value"], "green")
        self.assertEqual(values["DB_NAME"]["value"], "boarddb")
        self.assertEqual(values["APP_STORAGE_DIR"]["value"], "/var/smoke/attach")
        self.assertEqual(values["UPLOAD_DIR"]["value"], "/var/smoke/attach")
        self.assertEqual(pod["securityContext"]["runAsUser"], 1500)
        self.assertEqual(pod["securityContext"]["runAsGroup"], 1500)
        self.assertTrue(pod["securityContext"]["runAsNonRoot"])
        self.assertNotIn("ADMIN_PASSWORD", values)
        for k in ("DB_PASSWORD", "CHECK_TOKEN", "ADMIN_KEY"):
            self.assertNotIn("value", values[k])
            self.assertEqual(values[k]["valueFrom"]["secretKeyRef"]["key"], k)
        self.assertEqual(c["readinessProbe"]["httpGet"]["path"], "/health")
        self.assertEqual(c["volumeMounts"][0]["mountPath"], "/var/smoke/attach")
        self.assertEqual(pod["volumes"][0]["persistentVolumeClaim"]["claimName"], "smoke-attachments-pvc")
        self.assertEqual(spec["strategy"]["rollingUpdate"]["maxUnavailable"], 0)

    def test_blue_selector(self):
        c = self.config()
        c["slot"] = "blue"
        d = renderer.render(c)
        self.assertEqual(d["metadata"]["name"], "notice-blue")
        self.assertEqual(d["spec"]["template"]["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"], "smoke-attachments-pvc")

    def test_reject_different_pvc(self):
        c = self.config()
        c["pvc_name"] = "other-pvc"
        with self.assertRaises(ValueError):
            renderer.render(c)

    def test_reject_unpinned_image(self):
        c = self.config()
        c["image"] = c["image"].split("@")[0] + ":latest"
        with self.assertRaises(ValueError):
            renderer.render(c)

    def test_reject_secret_values_in_config(self):
        c = self.config()
        c["DB_PASSWORD"] = "not-a-real-password"
        with self.assertRaises(ValueError):
            renderer.render(c)

    def test_reject_example(self):
        import json
        p = Path(__file__).resolve().parents[1] / "config" / "notice-prod.example.json"
        with self.assertRaises(ValueError):
            renderer.render(json.loads(p.read_text()))

if __name__ == "__main__":
    unittest.main()
