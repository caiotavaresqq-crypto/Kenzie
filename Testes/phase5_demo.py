from pathlib import Path
from tempfile import TemporaryDirectory
from kenzie_cognition.learning_v2 import LearningPipeline
from kenzie_cognition.knowledge_store import KnowledgeStore

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    learner = LearningPipeline(root / "candidates.jsonl", root / "feedback.jsonl")
    store = KnowledgeStore(root / "knowledge.sqlite")
    learner.log_feedback("Explain lists", "A list is unordered", "Needs correction", "Lists preserve insertion order in Python", ["programming", "accuracy"])
    candidate = learner.propose("Python lists", "Lists preserve insertion order in Python", "Correction from supervised feedback", source="feedback", confidence=.85)
    print("Staged candidate:", candidate)
    print("Review is required before importing.")
    print("Accept candidate:", learner.review(candidate["candidate_id"], "accepted", store))
    print("Report:", learner.learning_report())
