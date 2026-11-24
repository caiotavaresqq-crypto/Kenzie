import json
import unittest
from types import SimpleNamespace
from action_engine_replanner import has_failures, replan_once


class FakeRegistry:
    def list_enabled(self):
        return [SimpleNamespace(id="open_url", description="Open URL", parameters={}),
                SimpleNamespace(id="open_app", description="Open app", parameters={})]


class FakeEngine:
    def __init__(self):
        self.registry = FakeRegistry()
    def function_schema(self):
        return [{"type": "function", "function": {"name": "create_action_plan", "parameters": {}}}]
    def build_plan(self, goal, steps):
        return {"goal": goal, "steps": steps}
    def execute(self, plan):
        return {"plan_id": "recovery-test", "goal": plan["goal"], "status": "success", "steps": [
            {"step_id": "step_1", "tool_id": "open_url", "parameters": {"url": "https://example.com"}, "status": "success", "result": {"ok": True}, "error": None}
        ]}


class FakeClient:
    def __init__(self, plan_args):
        self.plan_args = plan_args
        self.calls = 0
        function = SimpleNamespace(name="create_action_plan", arguments=json.dumps(plan_args))
        tool_call = SimpleNamespace(function=function)
        message = SimpleNamespace(tool_calls=[tool_call])
        choice = SimpleNamespace(message=message)
        self.response = SimpleNamespace(choices=[choice])
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
    def create(self, **kwargs):
        self.calls += 1
        return self.response



class ReplannerTests(unittest.TestCase):
    def test_failure_detection(self):
        self.assertTrue(has_failures({"steps": [{"status": "failed"}]}))
        self.assertTrue(has_failures({"steps": [{"status": "blocked"}]}))
        self.assertFalse(has_failures({"steps": [{"status": "success"}]}))
    def test_no_replan_without_failure(self):
        client = FakeClient({"goal": "recover", "steps": [{"tool_id": "open_url", "parameters": {"url": "https://example.com"}}]})
        self.assertIsNone(replan_once(FakeEngine(), client, "test-model", {"steps": [{"status": "success"}]}))
        self.assertEqual(client.calls, 0)
    def test_one_recovery_plan(self):
        failed_result = {"plan_id": "orig", "goal": "open page", "steps": [
            {"tool_id": "open_app", "parameters": {"app_name": "browser"}, "status": "failed"}
        ]}
        client = FakeClient({"goal": "recover open page", "steps": [{"tool_id": "open_url", "parameters": {"url": "https://example.com"}}]})
        result = replan_once(FakeEngine(), client, "test-model", failed_result)
        self.assertEqual(client.calls, 1)
        self.assertEqual(result["recovery_attempt"], 1)
        self.assertEqual(result["status"], "success")
    def test_rejects_same_failed_action(self):
        same = {"tool_id": "open_app", "parameters": {"app_name": "calculator"}}
        failed_result = {"plan_id": "orig", "goal": "open calculator", "steps": [{**same, "status": "failed"}]}
        client = FakeClient({"goal": "retry", "steps": [same]})
        result = replan_once(FakeEngine(), client, "test-model", failed_result)
        self.assertEqual(result["status"], "replan_rejected")
        self.assertEqual(client.calls, 1)


if __name__ == "__main__":
    unittest.main()
