"""Context utilities for bounded conversation history."""
from dataclasses import dataclass
from typing import Iterable, Any

@dataclass
class ContextWindow:
    recent_messages: list[dict]
    summary: str
    message_count: int
    truncated: bool

def normalize_message(item: Any) -> dict:
    if isinstance(item, dict):
        role = str(item.get("role", item.get("speaker", "unknown")))
        content = str(item.get("content", item.get("text", "")))
    else:
        role, content = "unknown", str(item)
    return {"role": role, "content": content.strip()}

def build_context_window(history: Iterable[Any], max_messages: int = 12, max_chars: int = 6000) -> ContextWindow:
    messages = [m for m in (normalize_message(x) for x in history) if m["content"]]
    recent = messages[-max(1, int(max_messages)):]
    out, chars = [], 0
    for msg in reversed(recent):
        line_len = len(msg["role"]) + len(msg["content"])
        if out and chars + line_len > max_chars:
            break
        content = msg["content"]
        if len(content) > max_chars:
            content = content[-max_chars:]
        out.append({"role": msg["role"], "content": content})
        chars += len(msg["role"]) + len(content)
    out.reverse()
    summary = "\n".join(f'{m["role"]}: {m["content"]}' for m in out)
    return ContextWindow(out, summary, len(messages), len(out) < len(messages))
