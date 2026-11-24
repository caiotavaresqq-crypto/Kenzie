"""Data models for Kenzie Action Engine 0.1."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class ActionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"

@dataclass
class ToolSpec:
    id: str
    name: str
    description: str
    category: str
    parameters: dict[str, Any]
    required_parameters: list[str]
    handler: Callable[..., Any]
    permissions: list[str] = field(default_factory=list)
    enabled: bool = True

@dataclass
class ActionStep:
    step_id: str
    tool_id: str
    parameters: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    status: ActionStatus = ActionStatus.PENDING
    result: Any = None
    error: Optional[str] = None

@dataclass
class ActionPlan:
    plan_id: str
    goal: str
    steps: list[ActionStep]
    status: ActionStatus = ActionStatus.PENDING
    requires_confirmation: bool = False
