import copy
import importlib.util
from pathlib import Path
import unittest

s = importlib.util.spec_from_file_location("planner", Path(__file__).with_name("notice-dynamic-plan.py"))
p = importlib.util.module_from_spec(s)
s.loader.exec_module(p)

class PlanTests(unittest.TestCase):
    groups = {"blue": "blue-arn", "green": "green-arn"}

    def actions(self, b, g):
        return [{"Type": "forward", "ForwardConfig": {"TargetGroups": [
            {"TargetGroupArn": "green-arn", "Weight": g}, {"TargetGroupArn": "blue-arn", "Weight": b}
        ], "TargetGroupStickinessConfig": {"Enabled": False}}}]

    def test_blue_active(self):
        self.assertEqual(p.select_slots(self.actions(100, 0), self.groups), ("blue", "green"))

    def test_green_active(self):
        self.assertEqual(p.select_slots(self.actions(0, 100), self.groups), ("green", "blue"))

    def test_reject_mixed_or_unexpected(self):
        for b, g in [(50, 50), (0, 0), (100, 100), (99, 0), (True, 0), ("100", 0)]:
            with self.subTest(b=b, g=g), self.assertRaises(ValueError):
                p.select_slots(self.actions(b, g), self.groups)

    def test_reject_stickiness(self):
        a = self.actions(100, 0)
        a[0]["ForwardConfig"]["TargetGroupStickinessConfig"]["Enabled"] = True
        with self.assertRaises(ValueError):
            p.select_slots(a, self.groups)

    def test_reject_wrong_target(self):
        a = self.actions(100, 0)
        a[0]["ForwardConfig"]["TargetGroups"][0]["TargetGroupArn"] = "other"
        with self.assertRaises(ValueError):
            p.select_slots(a, self.groups)

    def test_reject_duplicate_target(self):
        a = self.actions(100, 0)
        a[0]["ForwardConfig"]["TargetGroups"][0]["TargetGroupArn"] = "blue-arn"
        with self.assertRaises(ValueError):
            p.select_slots(a, self.groups)

    def test_reject_extra_action(self):
        a = self.actions(100, 0)
        with self.assertRaises(ValueError):
            p.select_slots(a + [{"Type": "redirect"}], self.groups)

    def test_plan_actions(self):
        self.assertEqual(p.plan_action("a", "b", ""), "DISCOVER_ONLY")
        self.assertEqual(p.plan_action("a", "b", "a"), "NOOP_ALREADY_ACTIVE")
        self.assertEqual(p.plan_action("a", "b", "b"), "VERIFY_EXISTING_CANDIDATE")
        self.assertEqual(p.plan_action("a", "b", "c"), "PLAN_UPDATE_INACTIVE")

if __name__ == "__main__":
    unittest.main()
