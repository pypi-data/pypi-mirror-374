from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class ToolCall:
    id: str
    name: str
    args: Dict[str, Any]

@dataclass
class AgentResponse:
    content: str
    tool_calls: List[ToolCall]