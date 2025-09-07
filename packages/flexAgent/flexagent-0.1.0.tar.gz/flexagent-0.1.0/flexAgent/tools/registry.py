from typing import List, Optional
from flexAgent.tools.base import ToolHandler

class ToolRegistry:
    def __init__(self):
        self._handlers: List[ToolHandler] = []

    def register(self, handler: ToolHandler):
        self._handlers.append(handler)

    def get_handler(self, tool_name: str) -> Optional[ToolHandler]:
        for handler in self._handlers:
            if handler.can_handle(tool_name):
                return handler
        return None

    def get_all_tools(self) -> List:
        tools = []
        for handler in self._handlers:
            if hasattr(handler, "get_tools"):
                tools.extend(handler.get_tools())
        return tools
