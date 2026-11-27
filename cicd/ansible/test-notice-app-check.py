import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("checker", Path(__file__).with_name("notice-app-check.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
COMMIT = "a" * 40

class Fake:
    def __init__(self, bad_read=False, bad_owner=False, bad_health=False):
        self.row = None
        self.deleted = False
        self.reads = 0
        self.bad_read, self.bad_owner, self.bad_health = bad_read, bad_owner, bad_health
        self.version = {"app": "haedeun-notice", "color": "green", "commit": COMMIT[:7], "version": "1.0.0"}

    def request(self, method, path, expected, body=None, auth=False):
        if path == "/health":
            value = dict(self.version, status="UP", db="UP", storage="DOWN" if self.bad_health else "UP")
        elif path == "/version":
            value = self.version
        elif path == "/notices" or path.startswith("/notices/"):
            return b"public list"
        elif not auth:
            assert expected == 401
            return b""
        elif method == "POST":
            self.row = dict(body, id=42, servedBy=self.version)
            value = self.row
        elif method == "DELETE":
            assert self.row is not None
            self.row = None
            self.deleted = True
            return b""
        elif self.row is None:
            assert expected == 404
            return b""
        else:
            self.reads += 1
            value = dict(self.row)
            if self.reads == 1 and self.bad_read:
                value["servedBy"] = dict(self.version, color="blue")
            if self.reads >= 2 and self.bad_owner:
                value["title"] = "unrelated notice"
        return json.dumps(value).encode()

class Tests(unittest.TestCase):
    def test_read_only(self):
        f = Fake()
        c.verify(f, "green", COMMIT)
        self.assertIsNone(f.row)
        self.assertFalse(f.deleted)

    def test_create_read_cleanup(self):
        f = Fake()
        c.verify(f, "green", COMMIT, True)
        self.assertTrue(f.deleted)
        self.assertIsNone(f.row)

    def test_failed_read_still_cleanup(self):
        f = Fake(bad_read=True)
        with self.assertRaises(c.CheckError):
            c.verify(f, "green", COMMIT, True)
        self.assertTrue(f.deleted)

    def test_refuse_wrong_cleanup_owner(self):
        f = Fake(bad_owner=True)
        with self.assertRaises(c.CheckError):
            c.verify(f, "green", COMMIT, True)
        self.assertFalse(f.deleted)

    def test_health_failure_no_create(self):
        f = Fake(bad_health=True)
        with self.assertRaises(c.CheckError):
            c.verify(f, "green", COMMIT, True)
        self.assertIsNone(f.row)

    def test_token_not_valid(self):
        with self.assertRaises(c.CheckError):
            c.Client(8080, "short")

if __name__ == "__main__":
    unittest.main()
