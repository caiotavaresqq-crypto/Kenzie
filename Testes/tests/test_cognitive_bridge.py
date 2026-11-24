import json
import os
import tempfile
import unittest
from pathlib import Path

from kenzie_cognition.pipeline import CognitivePipeline
from kenzie_cognition.integration import KenzieCognitiveAdapter
from cognitive_bridge import enabled


class CognitiveAdapterTests(unittest.TestCase):
    def test_prepare_preserves_history_and_adds_current_once(self):
        history = [{"role": "user", "content": "Estou programando em Python"},
                   {"role": "assistant", "content": "Certo."}]
        adapter = KenzieCognitiveAdapter(CognitivePipeline(), max_history_messages=20)
        prepared = adapter.prepare("Explique isso", history=history, system_prompt="SYSTEM")
        user_messages = [m for m in prepared.messages if m["role"] == "user"]
        self.assertEqual(len(user_messages), 2)
        self.assertEqual(user_messages[-1]["content"], "Explique isso")
        self.assertEqual(prepared.messages[0]["role"], "system")
        self.assertEqual(history[0]["content"], "Estou programando em Python")

    def test_adapter_handles_empty_history(self):
        prepared = KenzieCognitiveAdapter(CognitivePipeline()).prepare("Oi")
        self.assertEqual(prepared.messages[-1], {"role": "user", "content": "Oi"})

    def test_adapter_bounds_history(self):
        history = [{"role": "user", "content": f"message-{i}"} for i in range(10)]
        prepared = KenzieCognitiveAdapter(CognitivePipeline(), max_history_messages=3).prepare("current", history)
        self.assertEqual(len(prepared.messages), 5)  # system + 3 history + current
        self.assertEqual(prepared.messages[-1]["content"], "current")

    def test_disabled_flag_values(self):
        old = os.environ.get("KENZIE_COGNITION_ENABLED")
        try:
            for value in ("0", "false", "off", "no"):
                os.environ["KENZIE_COGNITION_ENABLED"] = value
                self.assertFalse(enabled())
            os.environ["KENZIE_COGNITION_ENABLED"] = "1"
            self.assertTrue(enabled())
        finally:
            if old is None:
                os.environ.pop("KENZIE_COGNITION_ENABLED", None)
            else:
                os.environ["KENZIE_COGNITION_ENABLED"] = old


if __name__ == "__main__":
    unittest.main()
