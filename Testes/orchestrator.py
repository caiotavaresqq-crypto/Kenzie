"""Central local-only orchestration for Kenzie 0.9."""
from dataclasses import dataclass
from typing import Any


@dataclass
class OrchestratorResult:
    messages: list[dict[str, Any]]
    cognitive_analysis: dict | None
    engine_status: dict


class KenzieOrchestrator:
    def __init__(self, local_engine, *, cognition_enabled=True):
        self.local_engine = local_engine
        self.cognition_enabled = bool(cognition_enabled)

    def prepare_turn(self, user_message: str, history, system_prompt: str, memory_text: str = "") -> OrchestratorResult:
        prior = []
        for item in list(history or [])[-20:]:
            if isinstance(item, dict) and item.get("role") in {"user", "assistant"} and item.get("content"):
                prior.append({"role": item["role"], "content": str(item["content"])})
        sys_text = str(system_prompt or "")
        if memory_text:
            sys_text += "\n\nLOCAL MEMORY (retrieved; relevance may be uncertain):\n" + memory_text
        analysis = None
        if self.cognition_enabled:
            try:
                from cognitive_bridge import prepare_cognitive_context
                prepared = prepare_cognitive_context(user_message, history=prior, system_prompt=sys_text)
                if prepared:
                    analysis = prepared.analysis.to_dict()
                    messages = prepared.messages
                else:
                    messages = [{"role": "system", "content": sys_text}] if sys_text else []
                    messages.extend(prior)
                    messages.append({"role": "user", "content": user_message})
            except Exception as exc:
                print(f"[Orchestrator] Cognitive Core não disponível: {type(exc).__name__}")
                messages = [{"role": "system", "content": sys_text}] if sys_text else []
                messages.extend(prior)
                messages.append({"role": "user", "content": user_message})
        else:
            messages = [{"role": "system", "content": sys_text}] if sys_text else []
            messages.extend(prior)
            messages.append({"role": "user", "content": user_message})
        return OrchestratorResult(messages, analysis, self.local_engine.status())
