#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import subprocess
spec = importlib.util.spec_from_file_location("publisher", Path(__file__).with_name("publish-release-sns.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class TestSNS(unittest.TestCase):
    def env(self):
        return dict(SMOKE_DEPLOY_SNS_TOPIC_ARN="arn:aws:sns:ap-northeast-2:000000000000:example-topic", JOB_NAME="smoke-notice-sns-test", BUILD_NUMBER="1")
    def test_subject(self):
        for outcome in m.LABELS:
            _, subject, body = m.build_message(self.env(), outcome)
            self.assertTrue(subject.startswith("[배포]"))
            self.assertLess(len(subject), 100)
            self.assertNotIn("\n", subject)
            self.assertEqual(body.splitlines()[0], subject)
            self.assertIn("Event ID:", body)
    def test_unknown(self):
        with self.assertRaises(ValueError): m.build_message(self.env(), "SUCCESS")
    def test_bad_topic(self):
        e = self.env(); e["SMOKE_DEPLOY_SNS_TOPIC_ARN"] = "wrong"
        with self.assertRaises(ValueError): m.build_message(e, "SMTP_RELAY_TEST")
    def test_bad_job(self):
        e = self.env(); e["JOB_NAME"] = "bad\njob"
        with self.assertRaises(ValueError): m.build_message(e, "SMTP_RELAY_TEST")
    @patch.object(m.subprocess, "run")
    def test_publish(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, "11111111-1111-1111-1111-111111111111\n", "")
        m.publish(self.env(), "SMTP_RELAY_TEST")
        self.assertEqual(run.call_count, 1)
        self.assertIn("--subject", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["env"]["AWS_MAX_ATTEMPTS"], "1")
    @patch.object(m.subprocess, "run")
    def test_failure(self, run):
        run.return_value = subprocess.CompletedProcess([], 1, "", "private error")
        with self.assertRaises(RuntimeError): m.publish(self.env(), "ROLLBACK_UNCONFIRMED")
        self.assertEqual(run.call_count, 1)
if __name__ == "__main__":
    unittest.main()
