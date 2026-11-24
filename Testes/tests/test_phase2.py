import unittest
from kenzie_cognition import classify_intent, build_context_window, detect_references, analyze_ambiguity, understand_message

class Phase2Tests(unittest.TestCase):
    def test_intent_create(self):
        result = classify_intent("Construa um módulo de memória")
        self.assertEqual(result.primary, "create")
        self.assertTrue(result.needs_action)
    def test_context_limits(self):
        history = [{"role":"user", "content":str(i)} for i in range(20)]
        window = build_context_window(history, max_messages=5)
        self.assertEqual(len(window.recent_messages), 5)
        self.assertEqual(window.recent_messages[-1]["content"], "19")
    def test_reference_detected(self):
        refs = detect_references("Pode corrigir isso?", [{"role":"assistant","content":"O script tem erro."}])
        self.assertTrue(any(r.token == "isso" for r in refs))
    def test_ambiguity_detected(self):
        report = analyze_ambiguity("Faz isso e aquela parte também")
        self.assertTrue(report.clarification_suggested)
    def test_unified_mode_clarify_missing_reference(self):
        result = understand_message("Corrige isso", [])
        self.assertEqual(result.suggested_response_mode, "clarify")
    def test_unified_mode_execute_clear(self):
        result = understand_message("Crie um arquivo para testar", [])
        self.assertEqual(result.suggested_response_mode, "execute")
if __name__ == "__main__":
    unittest.main()
