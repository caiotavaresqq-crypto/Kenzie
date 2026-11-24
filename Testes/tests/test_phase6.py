import tempfile
import unittest
from pathlib import Path
from kenzie_cognition.pipeline import CognitivePipeline
from kenzie_cognition.learning_v2 import LearningPipeline
from kenzie_cognition.knowledge_store import KnowledgeStore

class FakeKB:
    def search(self, query, limit=5):
        return [{"id": "x", "title": "API", "verified": False, "score": 0.8}]

class Phase6Tests(unittest.TestCase):
    def test_action_request_builds_problem_frame(self):
        result = CognitivePipeline().analyze("Crie um plano para meu aplicativo")
        self.assertIsNotNone(result.problem_frame)
        self.assertEqual(result.response_mode, "execute")

    def test_ambiguous_reference_requests_clarification(self):
        result = CognitivePipeline().analyze("Corrige isso")
        self.assertEqual(result.response_mode, "clarify")
        self.assertIsNone(result.problem_frame)

    def test_knowledge_is_context_not_fact(self):
        result = CognitivePipeline(knowledge_base=FakeKB()).analyze("Explique API")
        self.assertEqual(len(result.knowledge_matches), 1)
        self.assertTrue(any("unverified" in n for n in result.safety_notes))

    def test_empty_message_clarifies(self):
        result = CognitivePipeline().analyze("   ")
        self.assertEqual(result.response_mode, "clarify")

    def test_learning_requires_explicit_proposal_and_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            learning = LearningPipeline(Path(tmp)/"candidates.jsonl", Path(tmp)/"feedback.jsonl")
            store = KnowledgeStore(Path(tmp)/"knowledge.db")
            pipeline = CognitivePipeline(learning_pipeline=learning, knowledge_store=store)
            result = pipeline.analyze("Explique uma API")
            self.assertEqual(learning.learning_report()["candidate_total"], 0)
            candidate = pipeline.propose_learning(topic="API", content="Uma API define uma interface.", evidence="Fonte documental", confidence=0.6)
            reviewed = pipeline.review_learning(candidate["candidate_id"], "accepted")
            self.assertTrue(reviewed["ok"])
            self.assertEqual(store.search_topic("API")[0]["verified"], 0)

if __name__ == "__main__":
    unittest.main()
