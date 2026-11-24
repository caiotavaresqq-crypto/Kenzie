"""Lightweight Portuguese intent classification (heuristics, not an LLM)."""
from dataclasses import dataclass, asdict
import re
from typing import List


@dataclass
class IntentResult:
    primary: str
    secondary: List[str]
    confidence: float
    matched_signals: List[str]
    needs_action: bool

_RULES = {
    "create": [r"\b(cria|criar|crie|construa|construir|faz|fazer|desenvolve|desenvolver|implementa|implementar|escreve|escrever)\b"],
    "explain": [r"\b(explica|explicar|me explica|o que é|como funciona|por que|porque)\b"],
    "debug": [r"\b(erro|bug|exception|traceback|falhou|não funciona|nao funciona|corrige|corrigir|debug)\b"],
    "summarize": [r"\b(resume|resumir|resumo|sintetiza|sintetizar)\b"],
    "find_research": [r"\b(pesquisa|pesquisar|procura|procurar|busca|buscar|encontra|encontrar|verifica|verificar)\b"],
    "plan": [r"\b(planeja|planejar|plano|organiza|organizar|próximos passos|proximos passos|roadmap)\b"],
    "compare": [r"\b(compara|comparar|diferença|diferenca|melhor|versus|vs\.?|alternativas)\b"],
    "translate": [r"\b(traduz|traduzir|tradução|traducao)\b"],
    "conversation": [r"\b(oi|olá|ola|bom dia|boa tarde|boa noite|valeu|obrigado|obrigada)\b"],
}

def classify_intent(message: str) -> IntentResult:
    text = (message or "").strip().lower()
    matches = []
    signals = []
    for intent, patterns in _RULES.items():
        for pattern in patterns:
            if re.search(pattern, text):
                matches.append(intent)
                signals.append(pattern.replace(r"\b", ""))
                break
    if not matches:
        return IntentResult("unknown", [], 0.35, [], False)
    primary = matches[0]
    confidence = min(0.92, 0.52 + 0.14 * len(matches))
    if len(matches) > 1:
        confidence -= 0.04 * (len(matches)-1)
    return IntentResult(primary, matches[1:], round(max(0.35, confidence), 2), signals, primary not in {"conversation"})
