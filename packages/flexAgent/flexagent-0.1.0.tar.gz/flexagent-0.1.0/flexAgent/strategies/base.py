from abc import ABC, abstractmethod
from typing import List, Dict
from flexAgent.types.models import AgentResponse

class LLMStrategy(ABC):
    @abstractmethod
    def invoke(self, messages: List[Dict], tools: List) -> AgentResponse:
        pass

    @abstractmethod
    def bind_tools(self, tools: List) -> "LLMStrategy":
        pass