"""Reversible integration bridge for Kenzie's local cognitive modules.

The cognitive pipeline is advisory only: it cannot execute tools or override user
requests. The host now supplies a local inference backend by default; this bridge does not call any provider.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable

from kenzie_cognition.pipeline import CognitivePipeline
from kenzie_cognition.integration import KenzieCognitiveAdapter, PreparedTurn
from kenzie_cognition.knowledge_base import KnowledgeBase
from kenzie_cognition.knowledge_store import KnowledgeStore
from kenzie_cognition.learning_v2 import LearningPipeline

BASE_DIR = Path(__file__).resolve().parent
COGNITION_DIR = BASE_DIR / "cognition_data"
_adapter: KenzieCognitiveAdapter | None = None
_store: KnowledgeStore | None = None
_learning: LearningPipeline | None = None


def enabled() -> bool:
    return os.getenv("KENZIE_COGNITION_ENABLED", "1").strip().lower() not in {"0", "false", "off", "no"}


def _initialize() -> KenzieCognitiveAdapter:
    global _adapter, _store, _learning
    if _adapter is not None:
        return _adapter
    COGNITION_DIR.mkdir(parents=True, exist_ok=True)
    _store = KnowledgeStore(COGNITION_DIR / "kenzie_cognitive.db")
    _learning = LearningPipeline(
        candidates_path=COGNITION_DIR / "learning_candidates.jsonl",
        feedback_path=COGNITION_DIR / "feedback_journal.jsonl",
    )
    kb = KnowledgeBase(BASE_DIR / "knowledge_pack" / "domains")
    pipeline = CognitivePipeline(knowledge_base=kb, knowledge_store=_store, learning_pipeline=_learning)
    _adapter = KenzieCognitiveAdapter(pipeline, include_analysis=True, max_history_messages=20)
    return _adapter


def prepare_cognitive_context(user_message: str, history=None, system_prompt: str = "") -> PreparedTurn | None:
    """Return a cognitively enriched turn, or None when disabled/unavailable."""
    if not enabled():
        return None
    try:
        return _initialize().prepare(user_message, history=history, system_prompt=system_prompt)
    except Exception as exc:
        print(f"[Cognition] Pipeline indisponível; fluxo tradicional mantido ({type(exc).__name__}).")
        return None


def propose_learning_candidate(*, topic: str, content: str, evidence: str, source: str = "explicit_feedback", confidence: float = 0.5):
    """Stage a learning candidate for explicit human review; never auto-applies it."""
    if not enabled():
        raise RuntimeError("Cognitive integration is disabled")
    _initialize()
    return _learning.propose(topic=topic, content=content, evidence=evidence, source=source, confidence=confidence)



def review_learning_candidate(candidate_id: str, decision: str):
    """Accept/reject a staged candidate; accepted items remain unverified."""
    if not enabled():
        raise RuntimeError("Cognitive integration is disabled")
    _initialize()
    return _adapter.pipeline.review_learning(candidate_id, decision)



def log_cognitive_feedback(*, task: str, original_answer: str, feedback: str, corrected_answer: str = "", tags=None):
    if not enabled():
        raise RuntimeError("Cognitive integration is disabled")
    _initialize()
    return _learning.log_feedback(task, original_answer, feedback, corrected_answer, tags)
