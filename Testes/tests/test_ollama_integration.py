"""Optional real integration test; runs only when Ollama and the selected model exist."""
import unittest
from local_inference_engine import LocalInferenceEngine

engine = LocalInferenceEngine()
status = engine.status()

@unittest.skipUnless(status['available'], 'Ollama/model local indisponível neste ambiente; integração real não executada.')
class OllamaRealIntegrationTests(unittest.TestCase):
    def test_generate_real_local_reply(self):
        response = engine.generate([{'role':'user','content':'Responda em português em uma frase: 2 + 2?'}], tools=None, max_tokens=80)
        self.assertTrue(response.choices)
        self.assertTrue(response.choices[0].message.content.strip())

if __name__ == '__main__': unittest.main()
