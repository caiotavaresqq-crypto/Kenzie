"""Phase 5: safe learning pipeline based on feedback and reviewable candidates.

Does not train model weights or modify application behavior. It stages knowledge
proposals, deduplicates them, tracks review status, and summarizes feedback.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json



@dataclass
class LearningCandidate:
    topic: str
    content: str
    evidence: str
    source: str
    confidence: float
    created_at: str
    candidate_id: str
    status: str = "pending_review"



class LearningPipeline:
    STATUSES = {"pending_review", "accepted", "rejected"}


    def __init__(self, candidates_path="learning_candidates.jsonl", feedback_path="feedback_journal.jsonl"):
        self.candidates_path = Path(candidates_path)
        self.feedback_path = Path(feedback_path)
        self.candidates_path.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_path.parent.mkdir(parents=True, exist_ok=True)



    @staticmethod
    def _normalize(text):
        return " ".join(str(text).casefold().split())



    def propose(self, topic, content, evidence, source="feedback", confidence=0.5):
        topic, content, evidence = str(topic).strip(), str(content).strip(), str(evidence).strip()
        confidence = float(confidence)
        if not topic or not content or not evidence:
            raise ValueError("topic, content, and evidence must not be blank")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        digest = hashlib.sha256((self._normalize(topic) + "|" + self._normalize(content)).encode("utf-8")).hexdigest()[:16]
        existing = {c["candidate_id"] for c in self.list_candidates()}
        if digest in existing:
            return next(c for c in self.list_candidates() if c["candidate_id"] == digest)
        candidate = LearningCandidate(topic, content, evidence, str(source), confidence, datetime.now(timezone.utc).isoformat(), digest)
        with self.candidates_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(candidate), ensure_ascii=False) + "\n")
        return asdict(candidate)



    def list_candidates(self, status=None, limit=5000):
        if not self.candidates_path.exists():
            return []
        items = []
        with self.candidates_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if status is None or item.get("status") == status:
                    items.append(item)
        return items[-max(1, int(limit)):]



    def review(self, candidate_id, status, knowledge_store=None):
        if status not in self.STATUSES - {"pending_review"}:
            raise ValueError("review status must be accepted or rejected")
        candidates = self.list_candidates()
        found = next((c for c in candidates if c["candidate_id"] == candidate_id), None)
        if found is None:
            return {"ok": False, "reason": "candidate_not_found"}
        if found["status"] != "pending_review":
            return {"ok": False, "reason": "candidate_already_reviewed", "status": found["status"]}
        found["status"] = status
        found["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        # Rewrite atomically to preserve all candidate records and review state.
        tmp = self.candidates_path.with_suffix(self.candidates_path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for candidate in candidates:
                if candidate["candidate_id"] == candidate_id:
                    candidate.update(found)
                f.write(json.dumps(candidate, ensure_ascii=False) + "\n")
        tmp.replace(self.candidates_path)
        if status == "accepted" and knowledge_store is not None:
            entry_id = knowledge_store.add(found["topic"], found["content"], source=found["source"], confidence=found["confidence"], verified=False)
            return {"ok": True, "status": status, "knowledge_entry_id": entry_id}
        return {"ok": True, "status": status}



    def log_feedback(self, task, original_answer, feedback, corrected_answer="", tags=None):
        record = {
            "task": str(task), "original_answer": str(original_answer), "feedback": str(feedback),
            "corrected_answer": str(corrected_answer), "tags": list(tags or []),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with self.feedback_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record



    def feedback_summary(self):
        counts, tags, total = {}, {}, 0
        if self.feedback_path.exists():
            with self.feedback_path.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    total += 1
                    label = str(item.get("feedback", "unspecified")).strip().lower() or "unspecified"
                    counts[label] = counts.get(label, 0) + 1
                    for tag in item.get("tags", []):
                        tags[tag] = tags.get(tag, 0) + 1
        return {"total_feedback": total, "feedback_types": counts,
                "recurring_tags": sorted(tags.items(), key=lambda x: (-x[1], x[0]))}



    def learning_report(self):
        candidates = self.list_candidates()
        return {
            "candidate_total": len(candidates),
            "pending_review": sum(c["status"] == "pending_review" for c in candidates),
            "accepted": sum(c["status"] == "accepted" for c in candidates),
            "rejected": sum(c["status"] == "rejected" for c in candidates),
            "feedback": self.feedback_summary(),
            "policy": "Only reviewed accepted candidates can be added to knowledge; proposals never change model behavior by themselves."
        }
