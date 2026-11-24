"""Kenzie Action Engine 0.2: validated plans, sequential execution and audit trail."""
import json
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from action_engine_models import ActionPlan, ActionStep, ActionStatus
from action_engine_registry import ToolRegistry
from action_engine_tools import create_tool_specs


class ActionEngine:
    MAX_STEPS = 8



    def __init__(self, audit_path=None):
        self.registry = ToolRegistry()
        self.allowed_permissions = {"app.launch", "browser.open", "browser.search", "files.search"}
        self.audit_path = Path(audit_path) if audit_path else Path(__file__).with_name("action_engine_audit.jsonl")
        for spec in create_tool_specs():
            self.registry.register(spec)

    def function_schema(self):
        tools = []
        for spec in self.registry.list_enabled():
            tools.append({"type": "function", "function": {"name": spec.id, "description": spec.description, "parameters": spec.parameters}})
        tools.append({"type": "function", "function": {
            "name": "create_action_plan", "description": "Use para pedidos que exijam ações locais em uma ou mais etapas. Crie um plano em etapas usando somente IDs de ferramentas listadas. Não use para conversa normal.",
            "parameters": {"type": "object", "properties": {"goal": {"type": "string"}, "steps": {"type": "array", "items": {"type": "object", "properties": {"tool_id": {"type": "string"}, "parameters": {"type": "object"}, "depends_on": {"type": "array", "items": {"type": "integer"}}}, "required": ["tool_id", "parameters"]}}}, "required": ["goal", "steps"]}
        }})
        return tools

    def build_plan(self, goal, steps_data):
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("O objetivo do plano não pode ficar vazio.")
        if not isinstance(steps_data, list) or not steps_data:
            raise ValueError("O plano precisa conter pelo menos uma etapa.")
        if len(steps_data) > self.MAX_STEPS:
            raise ValueError(f"Planos estão limitados a {self.MAX_STEPS} etapas.")
        steps = []
        for i, raw in enumerate(steps_data, start=1):
            if not isinstance(raw, dict):
                raise ValueError(f"Etapa {i} inválida: esperado objeto.")
            tool_id = raw.get("tool_id", "")
            params = raw.get("parameters", {})
            spec = self.registry.get(tool_id)
            if not spec.enabled:
                raise ValueError(f"Ferramenta desabilitada: {tool_id}")
            self.registry.validate_parameters(spec, params)
            if not set(spec.permissions).issubset(self.allowed_permissions):
                raise PermissionError(f"Permissão não autorizada para {tool_id}")
            deps = raw.get("depends_on", [])
            if not isinstance(deps, list) or len(deps) != len(set(deps)):
                raise ValueError(f"Dependências inválidas na etapa {i}")
            if any(not isinstance(d, int) or isinstance(d, bool) or d < 1 or d >= i for d in deps):
                raise ValueError(f"Dependências inválidas na etapa {i}; só é possível depender de etapas anteriores.")
            steps.append(ActionStep(step_id=f"step_{i}", tool_id=tool_id, parameters=params, depends_on=[f"step_{d}" for d in deps]))
        return ActionPlan(plan_id=uuid.uuid4().hex[:10], goal=goal.strip(), steps=steps)



    def preview(self, plan: ActionPlan):
        """Return a safe preview without invoking any tool handlers."""
        return {"plan_id": plan.plan_id, "goal": plan.goal, "status": "preview", "steps": [
            {"step_id": s.step_id, "tool_id": s.tool_id, "parameters": dict(s.parameters), "depends_on": list(s.depends_on), "status": "pending"}
            for s in plan.steps
        ]}



    def _audit(self, plan_id, step_id, tool_id, status, elapsed_ms, error_type=None):
        # Intentionally excludes goal, arguments, URLs, file paths and result payloads.
        record = {"timestamp": datetime.now(timezone.utc).isoformat(), "plan_id": plan_id,
                  "step_id": step_id, "tool_id": tool_id, "status": status,
                  "elapsed_ms": round(elapsed_ms, 2)}
        if error_type:
            record["error_type"] = error_type
        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            # Audit failure should be visible in console, but not mask the action result.
            print("[ActionEngine] Não foi possível gravar o log de auditoria.")

    def execute(self, plan: ActionPlan):
        plan.status = ActionStatus.RUNNING
        by_id = {step.step_id: step for step in plan.steps}
        for step in plan.steps:
            if any(by_id[dep].status != ActionStatus.SUCCESS for dep in step.depends_on):
                step.status = ActionStatus.SKIPPED
                step.error = "Dependência não concluída."
                self._audit(plan.plan_id, step.step_id, step.tool_id, step.status.value, 0)
                continue
            step.status = ActionStatus.RUNNING
            started = time.perf_counter()
            try:
                spec = self.registry.get(step.tool_id)
                self.registry.validate_parameters(spec, step.parameters)
                if not spec.enabled or not set(spec.permissions).issubset(self.allowed_permissions):
                    step.status = ActionStatus.BLOCKED
                    step.error = "Ferramenta ou permissão bloqueada."
                else:
                    step.result = spec.handler(**step.parameters)
                    success = step.result.get("ok", False) if isinstance(step.result, dict) else False
                    step.status = ActionStatus.SUCCESS if success is True else ActionStatus.FAILED
                    if not success:
                        step.error = str(step.result)[:500]
            except Exception as exc:
                step.status = ActionStatus.FAILED
                step.error = f"{type(exc).__name__}: {str(exc)[:400]}"
            elapsed = (time.perf_counter() - started) * 1000
            self._audit(plan.plan_id, step.step_id, step.tool_id, step.status.value, elapsed,
                       (step.error.split(":", 1)[0] if ":" in step.error else "ToolFailure") if step.error else None)
        plan.status = ActionStatus.SUCCESS if all(s.status == ActionStatus.SUCCESS for s in plan.steps) else ActionStatus.FAILED
        return {"plan_id": plan.plan_id, "goal": plan.goal, "status": plan.status.value, "steps": [{"step_id": s.step_id, "tool_id": s.tool_id, "status": s.status.value, "result": s.result, "error": s.error} for s in plan.steps]}

    def execute_payload(self, payload):
        plan = self.build_plan(payload.get("goal", "Ação solicitada"), payload.get("steps", []))
        return self.execute(plan)



    @staticmethod
    def format_feedback(result):
        lines = [f"Plano: {result['goal']}", f"Status: {result['status']}"]
        for step in result["steps"]:
            lines.append(f"{step['step_id']} ({step['tool_id']}): {step['status']}")
            if step.get("result") is not None:
                rendered = json.dumps(step["result"], ensure_ascii=False) if isinstance(step["result"], dict) else str(step["result"])
                lines.append("  Resultado: " + rendered)
            if step.get("error"):
                lines.append(f"  Falha: {step['error']}")
        return "\n".join(lines)



ACTION_ENGINE = ActionEngine()
