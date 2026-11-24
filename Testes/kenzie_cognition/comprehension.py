"""Unified comprehension analysis: intent, context, references, ambiguity."""
from dataclasses import asdict, dataclass
from .intent import classify_intent
from .context import build_context_window
from .references import detect_references
from .ambiguity import analyze_ambiguity
@dataclass
class Comprehension:
    message: str
    intent: dict
    context: dict
    references: list[dict]
    ambiguity: dict
    suggested_response_mode: str

def understand_message(message: str, history=None, max_context_messages: int = 12) -> Comprehension:
    history = history or []
    intent = classify_intent(message)
    context = build_context_window(history, max_messages=max_context_messages)
    refs = detect_references(message, history)
    ambiguity = analyze_ambiguity(message)
    mode = "clarify" if ambiguity.clarification_suggested else ("execute" if intent.needs_action else "converse")
    # If detected references have no antecedent, prefer asking for clarification rather than guessing.
    if any(r.needs_clarification and r.candidate is None for r in refs):
        mode = "clarify"
    return Comprehension(message, asdict(intent), asdict(context), [asdict(r) for r in refs], asdict(ambiguity), mode)
