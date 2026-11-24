"""Kenzie Action Engine 0.1: plan validation, permissions and sequential execution."""
import json
import uuid
from action_engine_models import ActionPlan, ActionStep, ActionStatus
from action_engine_registry import ToolRegistry
from action_engine_tools import create_tool_specs

class ActionEngine:
    def __init__(self):
        self.registry = ToolRegistry()
        self.allowed_permissions = {"app.launch", "browser.open", "browser.search", "files.search"}
        for spec in create_tool_specs():
            self.registry.register(spec)

    def function_schema(self):
        tools = []
        for spec in self.registry.list_enabled():
            tools.append({"type": "function", "function": {"name": spec.id, "description": spec.description, "parameters": spec.parameters}})
        tools.append({"type": "function", "function": {
            "name": "create_action_plan", "description": "Use para pedidos que exigem uma ou mais ações locais. Crie um plano em etapas usando somente IDs de ferramentas listadas. Não use para conversa normal.",
            "parameters": {"type": "object", "properties": {"goal": {"type": "string"}, "steps": {"type": "array", "items": {"type": "object", "properties": {"tool_id": {"type": "string"}, "parameters": {"type": "object"}, "depends_on": {"type": "array", "items": {"type": "integer"}}}, "required": ["tool_id", "parameters"]}}}, "required": ["goal", "steps"]}
        }})
        return tools

    def build_plan(self, goal, steps_data):
        if not isinstance(steps_data, list) or not steps_data:
            raise ValueError("O plano precisa conter pelo menos uma etapa.")
        if len(steps_data) > 8:
            raise ValueError("Planos 0.1 estão limitados a 8 etapas.")
        steps = []
        for i, raw in enumerate(steps_data, start=1):
            tool_id = raw.get("tool_id", "")
            params = raw.get("parameters", {})
            spec = self.registry.get(tool_id)
            if not spec.enabled:
                raise ValueError(f"Ferramenta desabilitada: {tool_id}")
            self.registry.validate_parameters(spec, params)
            if not set(spec.permissions).issubset(self.allowed_permissions):
                raise PermissionError(f"Permissão não autorizada para {tool_id}")
            deps = raw.get("depends_on", [])
            if any(not isinstance(d, int) or d < 1 or d >= i for d in deps):
                raise ValueError(f"Dependências inválidas na etapa {i}")
            steps.append(ActionStep(step_id=f"step_{i}", tool_id=tool_id, parameters=params, depends_on=[f"step_{d}" for d in deps]))
        return ActionPlan(plan_id=uuid.uuid4().hex[:10], goal=goal, steps=steps)

    def execute(self, plan: ActionPlan):
        plan.status = ActionStatus.RUNNING
        by_id = {step.step_id: step for step in plan.steps}
        for step in plan.steps:
            if any(by_id[dep].status != ActionStatus.SUCCESS for dep in step.depends_on):
                step.status = ActionStatus.SKIPPED
                step.error = "Dependência não concluída."
                continue
            step.status = ActionStatus.RUNNING
            try:
                spec = self.registry.get(step.tool_id)
                self.registry.validate_parameters(spec, step.parameters)
                if not spec.enabled or not set(spec.permissions).issubset(self.allowed_permissions):
                    step.status = ActionStatus.BLOCKED
                    step.error = "Ferramenta ou permissão bloqueada."
                    continue
                step.result = spec.handler(**step.parameters)
                success = step.result.get("ok", True) if isinstance(step.result, dict) else not any(x in str(step.result).lower() for x in ("não consegui", "erro ao", "não encontrei"))
                step.status = ActionStatus.SUCCESS if success else ActionStatus.FAILED
                if not success:
                    step.error = str(step.result)
            except Exception as exc:
                step.status = ActionStatus.FAILED
                step.error = str(exc)
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
