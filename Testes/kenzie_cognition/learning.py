"""Supervised learning-from-feedback primitives. Does not modify source code."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path



@dataclass
class FeedbackRecord:
    task: str
    original_answer: str
    feedback: str
    corrected_answer: str = ""
    tags: list[str] | None = None
    created_at: str = ""



class FeedbackJournal:
    def __init__(self, path="feedback_journal.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)



    def append(self, task, original_answer, feedback, corrected_answer="", tags=None):
        record = FeedbackRecord(str(task), str(original_answer), str(feedback), str(corrected_answer), list(tags or []), datetime.now(timezone.utc).isoformat())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        return record



    def read_all(self, limit=2000):
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records[-max(1, int(limit)):]



    def improvement_summary(self):
        records = self.read_all()
        return {
            "feedback_count": len(records),
            "recurring_tags": _count_tags(records),
            "instruction": "Use feedback as evidence for improvement ideas. Review changes with tests and human approval before altering behavior.",
        }



def _count_tags(records):
    counts = {}
    for r in records:
        for tag in r.get("tags", []):
            counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))
