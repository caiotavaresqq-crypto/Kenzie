import tempfile
from pathlib import Path
import unittest
from kenzie_cognition import decompose_problem, format_problem_frame, review_answer, compare_options, KnowledgeStore, FeedbackJournal


class CognitiveTransferTests(unittest.TestCase):
    def test_problem_decomposition(self):
        frame = decompose_problem("Build a parser", "Input is JSON", ["No external dependencies"])
        text = format_problem_frame(frame)
        self.assertIn("Build a parser", text)
        self.assertIn("No external dependencies", text)

    def test_review_scores(self):
        review = review_answer(accuracy=5, relevance=4, completeness=4, clarity=4, calibration=4)
        self.assertEqual(review.total, 21)
        self.assertEqual(review.verdict, "strong")

    def test_option_scoring(self):
        result = compare_options([{"name":"A","cost":3,"reliability":5},{"name":"B","cost":5,"reliability":4}], {"cost":1,"reliability":2})
        self.assertEqual(result["ranked"][0]["name"], "A")

    def test_knowledge_store_and_feedback(self):
        with tempfile.TemporaryDirectory() as d:
            store = KnowledgeStore(Path(d)/"knowledge.db")
            entry_id = store.add("Python", "Lists are mutable", source="test", confidence=0.9)
            self.assertEqual(len(store.search_topic("Python")), 1)
            self.assertTrue(store.mark_verified(entry_id))
            journal = FeedbackJournal(Path(d)/"feedback.jsonl")
            journal.append("explain code", "bad answer", "Too vague", "more detail", tags=["clarity"])
            self.assertEqual(journal.improvement_summary()["recurring_tags"], [("clarity", 1)])

if __name__ == "__main__":
    unittest.main()
