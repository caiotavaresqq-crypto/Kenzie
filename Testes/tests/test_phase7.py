import unittest
from kenzie_cognition.pipeline import CognitivePipeline
from kenzie_cognition.integration import KenzieCognitiveAdapter

class Phase7Tests(unittest.TestCase):
    def test_prepare_preserves_original_message_and_history(self):
        history = [{"role": "user", "content": "Estou criando um app"}]
        snapshot = [dict(x) for x in history]
        adapter = KenzieCognitiveAdapter(CognitivePipeline())
        turn = adapter.prepare("Explique isso", history, "Você é Kenzie")
        self.assertEqual(history, snapshot)
        self.assertEqual(turn.messages[-1], {"role": "user", "content": "Explique isso"})
        self.assertTrue(turn.messages[0]["content"].startswith("Você é Kenzie"))

    def test_model_call_is_host_supplied(self):
        adapter = KenzieCognitiveAdapter(CognitivePipeline())
        seen = {}
        def fake_model(messages):
            seen["messages"] = messages
            return "resposta simulada"
        response, prepared = adapter.run("Olá", fake_model)
        self.assertEqual(response, "resposta simulada")
        self.assertEqual(seen["messages"][-1]["content"], "Olá")

    def test_can_disable_analysis_injection(self):
        adapter = KenzieCognitiveAdapter(CognitivePipeline(), include_analysis=False)
        turn = adapter.prepare("Oi", system_prompt="Base")
        self.assertEqual(turn.messages[0]["content"], "Base")

if __name__ == "__main__":
    unittest.main()
