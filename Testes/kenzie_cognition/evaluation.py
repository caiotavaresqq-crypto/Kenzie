"""Answer-quality evaluation rubric and decision helpers."""
from dataclasses import dataclass

from typing import Dict, List



@dataclass
class Review:
    accuracy: int
    relevance: int
    completeness: int
    clarity: int
    calibration: int
    notes: List[str]

    @property
    def total(self) -> int:
        vals = [self.accuracy, self.relevance, self.completeness, self.clarity, self.calibration]
        if any(v < 0 or v > 5 for v in vals):
            raise ValueError("Scores must be from 0 through 5")
        return sum(vals)

    @property
    def verdict(self) -> str:
        score = self.total
        return "strong" if score >= 21 else "usable_with_revision" if score >= 15 else "needs_rework"


def review_answer(*, accuracy: int, relevance: int, completeness: int, clarity: int, calibration: int, notes=None) -> Review:
    review = Review(accuracy, relevance, completeness, clarity, calibration, list(notes or []))
    _ = review.total  # validates scores
    return review



def compare_options(options: List[Dict], weights: Dict[str, float] | None = None) -> dict:
    """Transparent weighted comparison. Each option must have numeric criterion values."""
    weights = weights or {}
    if not options:
        return {"ranked": [], "warning": "No options supplied."}
    criteria = list(weights) or sorted({k for o in options for k, v in o.items() if k != "name" and isinstance(v, (int, float))})
    if not criteria:
        return {"ranked": [], "warning": "No numeric criteria supplied."}
    total_weight = sum(float(weights.get(c, 1.0)) for c in criteria)
    if total_weight <= 0:
        raise ValueError("Total criterion weight must be positive")
    ranked = []
    for option in options:
        score = sum(float(option.get(c, 0)) * float(weights.get(c, 1.0)) for c in criteria) / total_weight
        ranked.append({"name": option.get("name", "unnamed"), "score": round(score, 4), "criteria_used": criteria})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {"ranked": ranked, "warning": "Scores are only as reliable as the inputs; verify important decisions independently."}
