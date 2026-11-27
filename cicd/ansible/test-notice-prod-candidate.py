#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("candidate", Path(__file__).with_name("notice-prod-candidate.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class PatchTest(unittest.TestCase):
    def setUp(self):
        self.want = m.load_renderer().render(dict(slot="green", image="123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/smoke-notice@sha256:"+"a"*64, commit="b"*40, db_host="example.ap-northeast-2.rds.amazonaws.com", db_user="boarduser", secret_name="smoke-notice-secret", pvc_name="smoke-attachments-pvc"))
        self.old = {"metadata":{"name":"notice-green","resourceVersion":"123"},"spec":{"replicas":2,"selector":self.want["spec"]["selector"],"template":{"spec":{"containers":[{"name":"notice","image":"old"}]}}}}
    def test_guarded_patch(self):
        patch = m.make_patch(self.old,self.want)
        self.assertEqual(patch[0],{"op":"test","path":"/metadata/resourceVersion","value":"123"})
        self.assertEqual(patch[3]["value"],self.want["spec"]["template"])
        self.assertNotIn("FILE_BASE_URL", str(patch))
        self.assertNotIn("value': 'DB_PASSWORD",str(patch))
    def test_reject_blue(self):
        self.want["metadata"]["name"]="notice-blue"
        with self.assertRaises(ValueError): m.make_patch(self.old,self.want)
    def test_reject_selector_change(self):
        self.old["spec"]["selector"]={}
        with self.assertRaises(ValueError): m.make_patch(self.old,self.want)
    def test_reject_replica_change(self):
        self.old["spec"]["replicas"]=1
        with self.assertRaises(ValueError): m.make_patch(self.old,self.want)
if __name__ == "__main__": unittest.main()
