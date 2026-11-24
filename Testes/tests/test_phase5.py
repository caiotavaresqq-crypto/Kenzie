import tempfile
import unittest
from pathlib import Path
from kenzie_cognition.learning_v2 import LearningPipeline
from kenzie_cognition.knowledge_store import KnowledgeStore


class Phase5Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pipeline = LearningPipeline(self.root / "candidates.jsonl", self.root / "feedback.jsonl")
        self.store = KnowledgeStore(self.root / "knowledge.sqlite")
    def tearDown(self):
        self.temp.cleanup()
    def test_candidate_starts_pending(self):
        c = self.pipeline.propose("Python", "Lists are ordered collections", "Python docs", confidence=.9)
        self.assertEqual(c["status"], "pending_review")
    def test_deduplicates_case_and_whitespace(self):
        first = self.pipeline.propose("Python", "Lists are ordered collections", "source A")
        second = self.pipeline.propose(" python ", " lists are ordered collections ", "source B")
        self.assertEqual(first["candidate_id"], second["candidate_id"])
        self.assertEqual(len(self.pipeline.list_candidates()), 1)
    def test_requires_evidence(self):
        with self.assertRaises(ValueError):
            self.pipeline.propose("topic", "content", "")
    def test_confidence_range(self):
        with self.assertRaises(ValueError):
            self.pipeline.propose("t", "c", "e", confidence=1.5)
    def test_rejected_not_imported(self):
        c = self.pipeline.propose("Topic", "Candidate fact", "Evidence")
        result = self.pipeline.review(c["candidate_id"], "rejected", self.store)
        self.assertTrue(result["ok"])
        self.assertEqual(self.store.search_topic("Topic"), [])
    def test_accepted_imports_unverified(self):
        c = self.pipeline.propose("Topic", "Candidate fact", "Evidence", confidence=.8)
        result = self.pipeline.review(c["candidate_id"], "accepted", self.store)
        self.assertTrue(result["ok"])
        item = self.store.search_topic("Topic")[0]
        self.assertEqual(item["verified"], 0)
        self.assertEqual(item["confidence"], .8)
    def test_double_review_blocked(self):
        c = self.pipeline.propose("T", "C", "E")
        self.pipeline.review(c["candidate_id"], "accepted")
        result = self.pipeline.review(c["candidate_id"], "rejected")
        self.assertEqual(result["reason"], "candidate_already_reviewed")
    def test_feedback_aggregation(self):
        self.pipeline.log_feedback("task", "wrong", "correction", "right", ["math", "format"])
        self.pipeline.log_feedback("task2", "bad", "correction", "good", ["math"])
        summary = self.pipeline.feedback_summary()
        self.assertEqual(summary["total_feedback"], 2)
        self.assertEqual(summary["recurring_tags"][0], ("math", 2))
    def test_report_counts(self):
        self.pipeline.propose("T1", "C1", "E1")
        c = self.pipeline.propose("T2", "C2", "E2")
        self.pipeline.review(c["candidate_id"], "accepted")
        report = self.pipeline.learning_report()
        self.assertEqual(report["pending_review"], 1)
        self.assertEqual(report["accepted"], 1)

if __name__ == "__main__":
    unittest.main()
