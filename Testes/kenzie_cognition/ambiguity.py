"""Transparent ambiguity flags to guide follow-up questions."""
from dataclasses import dataclass
import re
from typing import List
@dataclass
class AmbiguityReport:
    score: float
    flags: List[str]
    clarification_suggested: bool
    question: str | None

VAGUE = ["isso", "aquilo", "aquela coisa", "o negócio", "a parte", "ele", "ela", "lá", "dessa"]

def analyze_ambiguity(message: str) -> AmbiguityReport:
    text = (message or "").strip().lower()
    flags = []
    if not text:
        return AmbiguityReport(1.0, ["empty_message"], True, "O que você quer fazer?")
    if any(re.search(rf"\b{re.escape(v)}\b", text) for v in VAGUE):
        flags.append("possible_unresolved_reference")
    if len(re.findall(r"\b(e|ou|também|alem disso|além disso)\b", text)) >= 3:
        flags.append("multiple_requests_or_topics")
    if len(text) < 5 and text not in {"oi", "ola", "olá", "ok", "sim", "não", "nao"}:
        flags.append("very_short_message")
    if text.endswith("...") or text.endswith("?") and len(text.split()) <= 3:
        flags.append("underspecified_request")
    score = min(1.0, 0.25 * len(flags))
    suggest = score >= 0.25
    question = "Pode especificar a que você está se referindo?" if "possible_unresolved_reference" in flags else ("Qual parte você quer priorizar?" if "multiple_requests_or_topics" in flags else None)
    return AmbiguityReport(round(score, 2), flags, suggest, question)
