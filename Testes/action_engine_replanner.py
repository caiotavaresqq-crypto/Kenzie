"""Bounded, LLM-assisted recovery for Kenzie Action Engine 0.3.

The replanner is intentionally single-shot. It proposes a recovery-only plan and
never executes arbitrary model-generated code. All proposed tools/parameters are
validated by ActionEngine.build_plan before execution.
"""
from __future__ import annotations
import json
from typing import Any

MAX_RECOVERY_STEPS = 4


def _signature(step: dict[str, Any]) -> str:
    return json.dumps(
        {"tool_id": step.get("tool_id"), "parameters": step.get("parameters", {})},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    )


def has_failures(result: dict[str, Any]) -> bool:
    return any(s.get("status") in {"failed", "blocked"} for s in result.get("steps", []))



def replan_once(engine, client, model: str, result: dict[str, Any]) -> dict[str, Any] | None:
    """Ask the configured LLM for one recovery plan; return None if not applicable."""
    if client is None or not has_failures(result):
        return None
    steps = result.get("steps", [])
    failed = [s for s in steps if s.get("status") in {"failed", "blocked"}]
    succeeded = [s for s in steps if s.get("status") == "success"]
    if not failed:
        return None
    if len(failed) > 4:
        failed = failed[:4]

    succeeded_signatures = {_signature(s) for s in succeeded}
    failed_signatures = {_signature(s) for s in failed}
    tool_defs = engine.function_schema()
    plan_tool = next((t for t in tool_defs if t.get("function", {}).get("name") == "create_action_plan"), None)
    if plan_tool is None:
        return None

    tool_catalog = [
        {"id": spec.id, "description": spec.description, "parameters": spec.parameters}
        for spec in engine.registry.list_enabled()
    ]
    recovery_prompt = (
        "Ferramentas disponíveis (use apenas estas):\n" +
        json.dumps(tool_catalog, ensure_ascii=False) + "\n\n" +
        "Você é o mecanismo de recuperação da Kenzie Action Engine. Analise o resultado real abaixo. "
        "Proponha no máximo 4 etapas de recuperação, usando somente ferramentas registradas. "
        "Não repita etapas que já tiveram sucesso e não repita uma ação falha com os mesmos parâmetros. "
        "Não tente contornar permissões, não invente ferramentas, não gere código e não crie ações "
        "destrutivas. Se não houver alternativa útil, não solicite plano. O plano deve tratar apenas " 
        "o objetivo ainda não concluído. Resultado anterior (JSON):\n" +
        json.dumps(result, ensure_ascii=False, default=str)[:12000]
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": recovery_prompt},
                {"role": "user", "content": "Se existir alternativa válida, proponha um plano de recuperação. Caso contrário, responda normalmente explicando que não há alternativa."},
            ],
            tools=[plan_tool],
            tool_choice={"type": "function", "function": {"name": "create_action_plan"}},
            temperature=0.2,
            max_tokens=500,
        )
        if not response.choices:
            return None
        calls = response.choices[0].message.tool_calls or []
        if len(calls) != 1 or calls[0].function.name != "create_action_plan":
            return None
        payload = json.loads(calls[0].function.arguments or "{}")
        proposed = payload.get("steps", [])
        if not isinstance(proposed, list) or not proposed or len(proposed) > MAX_RECOVERY_STEPS:
            return None
        proposed_signatures = {_signature(s) for s in proposed if isinstance(s, dict)}
        if proposed_signatures & succeeded_signatures:
            return {"status": "replan_rejected", "reason": "O plano de recuperação repetiria uma etapa já concluída."}
        if proposed_signatures & failed_signatures:
            return {"status": "replan_rejected", "reason": "O plano de recuperação repetiria uma etapa que falhou."}
        recovery_plan = engine.build_plan(
            str(payload.get("goal") or "Recuperar tarefa parcialmente concluída"), proposed
        )
        # Additional runtime guard: recovery plans are only allowed to contain registered,
        # enabled tools and validated parameters (build_plan performs these checks).
        recovery_result = engine.execute(recovery_plan)
        recovery_result["recovery_attempt"] = 1
        recovery_result["recovery_for"] = result.get("plan_id")
        return recovery_result
    except Exception as exc:
        return {"status": "replan_failed", "reason": f"{type(exc).__name__}: {str(exc)[:250]}"}
