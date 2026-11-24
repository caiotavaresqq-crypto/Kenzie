"""Detect references and cautiously resolve them against recent history."""
from dataclasses import dataclass
import re
from typing import Iterable, Any
from .context import normalize_message


@dataclass
class Reference:
    token: str
    kind: str
    candidate: str | None
    source_role: str | None
    confidence: float
    needs_clarification: bool

_PRONOUNS = {
    "isso": "thing", "isto": "thing", "esse": "thing", "essa": "thing", "este": "thing", "esta": "thing",
    "ele": "person_or_object", "ela": "person_or_object", "eles": "plural", "elas": "plural",
    "aquele": "thing", "aquela": "thing", "aqui": "place_or_context", "lá": "place_or_context", "la": "place_or_context",
    "dele": "possessive", "dela": "possessive", "desse": "possessive", "dessa": "possessive",
}

def detect_references(message: str, history: Iterable[Any] = ()) -> list[Reference]:
    found = []
    normalized_history = [normalize_message(x) for x in history]
    prior = next((m for m in reversed(normalized_history) if m["content"]), None)
    for token, kind in _PRONOUNS.items():
        if re.search(rf"\b{re.escape(token)}\b", (message or "").lower()):
            candidate = None
            confidence = 0.35
            role = None
            if prior:
                # The immediately prior message is only a candidate source, not guaranteed antecedent.
                candidate = prior["content"][-180:].strip()
                role = prior["role"]
                confidence = 0.48
            found.append(Reference(token, kind, candidate, role, confidence, candidate is None or confidence < 0.7))
    return found
