import tempfile
import unittest
from pathlib import Path

from action_engine import ActionEngine
from action_engine_models import ToolSpec, ActionStatus


class ActionEngineTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.engine = ActionEngine(audit_path=Path(self.tempdir.name) / "audit.jsonl")
        self.engine.registry.register(ToolSpec(
            id="test_ok", name="test", description="test tool", category="test",
            parameters={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
            required_parameters=["value"], handler=lambda value: {"ok": True, "value": value}, permissions=[]
        ))
        self.engine.registry.register(ToolSpec(
            id="test_fail", name="test fail", description="failing tool", category="test",
            parameters={"type": "object", "properties": {}, "required": []},
            required_parameters=[], handler=lambda: {"ok": False, "message": "test failure"}, permissions=[]
        ))

    def tearDown(self):
        self.tempdir.cleanup()



    def test_preview_does_not_execute(self):
        plan = self.engine.build_plan("preview", [{"tool_id": "test_ok", "parameters": {"value": "x"}}])
        preview = self.engine.preview(plan)
        self.assertEqual(preview["status"], "preview")
        self.assertEqual(plan.steps[0].status, ActionStatus.PENDING)
        self.assertFalse(Path(self.tempdir.name, "audit.jsonl").exists())



    def test_failure_skips_dependent_step(self):
        plan = self.engine.build_plan("test", [
            {"tool_id": "test_fail", "parameters": {}},
            {"tool_id": "test_ok", "parameters": {"value": "x"}, "depends_on": [1]},
        ])
        result = self.engine.execute(plan)
        self.assertEqual(result["steps"][0]["status"], "failed")
        self.assertEqual(result["steps"][1]["status"], "skipped")
        self.assertEqual(result["status"], "failed")
        self.assertTrue(Path(self.tempdir.name, "audit.jsonl").exists())



    def test_invalid_dependency_rejected(self):
        with self.assertRaises(ValueError):
            self.engine.build_plan("invalid", [{"tool_id": "test_ok", "parameters": {"value": "x"}, "depends_on": [1]}])



    def test_success_plan(self):
        plan = self.engine.build_plan("success", [{"tool_id": "test_ok", "parameters": {"value": "hello"}}])
        result = self.engine.execute(plan)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["steps"][0]["result"]["value"], "hello")



if __name__ == "__main__":
    unittest.main()
