import unittest
from unittest.mock import patch, MagicMock
from research_engine import ResearchEngine, _TextExtractor, _public_http_url, _public_http_url

class ResearchTests(unittest.TestCase):
    def test_html_text_extraction_skips_script(self):
        parser = _TextExtractor()
        parser.feed('<h1>Title</h1><p>Body text</p><script>secret()</script>')
        result = parser.text()
        self.assertIn('Title', result)
        self.assertIn('Body text', result)
        self.assertNotIn('secret', result)

    def test_private_and_local_targets_are_blocked(self):
        self.assertFalse(_public_http_url('http://127.0.0.1:8080/'))
        self.assertFalse(_public_http_url('http://localhost/'))
        self.assertFalse(_public_http_url('http://192.168.1.10/'))

    def test_public_ip_is_accepted(self):
        self.assertTrue(_public_http_url('https://8.8.8.8/'))

    def test_private_and_local_targets_are_blocked(self):
        self.assertFalse(_public_http_url('http://127.0.0.1:8080/'))
        self.assertFalse(_public_http_url('http://localhost/'))
        self.assertFalse(_public_http_url('http://192.168.1.10/'))

    def test_public_ip_is_accepted(self):
        self.assertTrue(_public_http_url('https://8.8.8.8/'))

    def test_empty_query_is_rejected(self):
        self.assertFalse(ResearchEngine().search('')['ok'])

    @patch('research_engine._public_http_url', return_value=True)
    @patch('research_engine._SAFE_OPENER.open')
    def test_research_reads_result_when_robots_allows(self, opener, _public):
        search = MagicMock(); search.__enter__.return_value.read.return_value = b'<a class="result__a" href="https://example.org/page">Example result</a>'
        robots = MagicMock(); robots.__enter__.return_value.read.return_value = b'User-agent: *\nAllow: /\n'
        page = MagicMock(); page.__enter__.return_value.headers.get.return_value = 'text/html'; page.__enter__.return_value.read.return_value = b'<h1>Page title</h1><p>Useful content</p>'
        opener.side_effect = [search, robots, page]
        result = ResearchEngine().search('sample query')
        self.assertTrue(result['ok'])
        self.assertIn('Useful content', result['results'][0]['content'])
        self.assertEqual(result['source_type'], 'external_research')

    @patch('urllib.request.urlopen', side_effect=OSError('network disabled'))
    def test_offline_search_reports_clear_failure(self, _mock):
        result = ResearchEngine().search('test query')
        self.assertFalse(result['ok'])
        self.assertIn('indisponível', result['error'])

if __name__ == '__main__': unittest.main()
