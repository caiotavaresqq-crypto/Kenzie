"""Tool Registry: dynamic registration and validation for the Action Engine."""
from typing import Any
from action_engine_models import ToolSpec


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec, replace: bool = False) -> None:
        if spec.id in self._tools and not replace:
            raise ValueError(f"Tool '{spec.id}' já registrada.")
        self._tools[spec.id] = spec

    def remove(self, tool_id: str) -> bool:
        return self._tools.pop(tool_id, None) is not None

    def enable(self, tool_id: str, enabled: bool = True) -> None:
        self.get(tool_id).enabled = enabled

    def get(self, tool_id: str) -> ToolSpec:
        if tool_id not in self._tools:
            raise KeyError(f"Ferramenta desconhecida: {tool_id}")
        return self._tools[tool_id]

    def list_enabled(self) -> list[ToolSpec]:
        return [tool for tool in self._tools.values() if tool.enabled]


    def validate_parameters(self, tool: ToolSpec, params: dict[str, Any]) -> None:
        if not isinstance(params, dict):
            raise ValueError("Os parâmetros precisam ser um objeto.")
        unknown = set(params) - set(tool.parameters.get("properties", {}))
        if unknown:
            raise ValueError(f"Parâmetros não reconhecidos: {', '.join(sorted(unknown))}")
        missing = [name for name in tool.required_parameters if name not in params]
        if missing:
            raise ValueError(f"Parâmetros obrigatórios ausentes: {', '.join(missing)}")
        for name, value in params.items():
            expected = tool.parameters.get("properties", {}).get(name, {}).get("type")
            if expected == "string" and not isinstance(value, str):
                raise ValueError(f"'{name}' deve ser texto.")
            if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
                raise ValueError(f"'{name}' deve ser inteiro.")
