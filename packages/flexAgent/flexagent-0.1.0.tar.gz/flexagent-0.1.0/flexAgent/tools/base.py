from abc import ABC, abstractmethod
from typing import Any, Dict
from flexAgent.types.models import ToolCall

class ToolHandler(ABC):
    @abstractmethod
    def can_handle(self, tool_name: str) -> bool:
        pass

    @abstractmethod
    def execute(self, tool_call: ToolCall, config: Dict) -> Dict[str, Any]:
        pass
