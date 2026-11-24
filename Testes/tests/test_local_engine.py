import unittest
from unittest.mock import patch, MagicMock
from local_inference_engine import LocalInferenceEngine, LocalEngineConfig
from orchestrator import KenzieOrchestrator

class LocalEngineTests(unittest.TestCase):
    def test_env_model_default_config_object(self):
        config = LocalEngineConfig(model='qwen2.5:1.5b')
        engine = LocalInferenceEngine(config)
        self.assertEqual(engine.config.model, 'qwen2.5:1.5b')
        self.assertEqual(engine.config.temperature, 0.7)

    @patch('urllib.request.urlopen')
    def test_healthcheck_available_when_ollama_tags_endpoint_responds(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b'{"models":[{"name":"qwen2.5:1.5b"}]}'
        engine = LocalInferenceEngine(LocalEngineConfig())
        engine._client = object()  # health-check only; SDK call path is mocked by this test
        self.assertTrue(engine.is_available())

    @patch('urllib.request.urlopen')
    def test_model_missing_is_not_available(self, mock_urlopen):
        response = mock_urlopen.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b'{"models":[{"name":"other-model:latest"}]}'
        engine = LocalInferenceEngine(LocalEngineConfig())
        engine._client = object()
        self.assertFalse(engine.is_available())
        self.assertFalse(engine.status()['model_available'])

    @patch('urllib.request.urlopen', side_effect=OSError('offline'))
    def test_healthcheck_offline_returns_false(self, _mock):
        engine = LocalInferenceEngine(LocalEngineConfig())
        self.assertFalse(engine.is_available())

    def test_generate_uses_configured_local_model_and_local_client(self):
        engine = LocalInferenceEngine(LocalEngineConfig(model='test-local-model'))
        fake_completion = MagicMock()
        fake_completion.chat.completions.create.return_value = 'local response'
        engine._client = fake_completion
        with patch.object(engine, 'is_available', return_value=True):
            response = engine.generate([{'role':'user','content':'hi'}], temperature=0.3, max_tokens=77)
        self.assertEqual(response, 'local response')
        kwargs = fake_completion.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs['model'], 'test-local-model')
        self.assertEqual(kwargs['temperature'], 0.3)
        self.assertEqual(kwargs['max_tokens'], 77)
        self.assertEqual(kwargs['messages'][0]['content'], 'hi')

    def test_orchestrator_keeps_history_and_adds_current_turn(self):
        fake_engine = MagicMock()
        fake_engine.status.return_value = {'available': False, 'model': 'test'}
        orchestrator = KenzieOrchestrator(fake_engine, cognition_enabled=False)
        prepared = orchestrator.prepare_turn('oi', [{'role':'user','content':'antes'}], 'prompt base', 'memoria')
        self.assertEqual(prepared.messages[0]['role'], 'system')
        self.assertIn('memoria', prepared.messages[0]['content'])
        self.assertEqual(prepared.messages[-1], {'role':'user','content':'oi'})

if __name__ == '__main__': unittest.main()
