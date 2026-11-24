import unittest
from pathlib import Path

class ExternalProviderDisabledTests(unittest.TestCase):
    def test_main_chat_has_no_remote_provider_endpoint_or_client_creation(self):
        source = Path(__file__).resolve().parents[1] / 'Kenzie.py'
        code = source.read_text(encoding='utf-8')
        self.assertNotIn('https://openrouter.ai/api/v1', code)
        self.assertNotIn('OpenAI(api_key=', code)
        self.assertIn('openrouter_client = None', code)
        self.assertIn('openai_client = None', code)

if __name__ == '__main__': unittest.main()
