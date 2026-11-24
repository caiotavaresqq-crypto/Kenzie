import tempfile
import unittest
from pathlib import Path
from kenzie_cognition.knowledge_base import KnowledgeBase
from kenzie_cognition.knowledge_store import KnowledgeStore


class Phase4Tests(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase()

    def test_pack_has_multiple_domains_and_items(self):
        self.assertGreaterEqual(len(self.kb.entries), 30)
        self.assertGreaterEqual(len(self.kb.domains()), 5)

    def test_search_finds_debugging(self):
        results = self.kb.search("debug error traceback fix", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "prog-006")

    def test_search_domain_filter(self):
        results = self.kb.search("functions and variables", domain="programming")
        self.assertTrue(results)
        self.assertTrue(all(r["domain"] == "programming" for r in results))

    def test_blank_query(self):
        self.assertEqual(self.kb.search("   "), [])

    def test_import_is_repeat_safe_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = KnowledgeStore(Path(tmp) / "kb.sqlite")
            first = self.kb.import_into_store(store)
            second = self.kb.import_into_store(store)
            self.assertEqual(first["imported"], len(self.kb.entries))
            self.assertEqual(second["imported"], 0)
            self.assertEqual(second["skipped"], len(self.kb.entries))

    def test_domain_names(self):
        domains = self.kb.domains()
        self.assertIn("programming", domains)
        self.assertIn("mathematics", domains)
        self.assertIn("sciences", domains)


if __name__ == "__main__":
    unittest.main()
