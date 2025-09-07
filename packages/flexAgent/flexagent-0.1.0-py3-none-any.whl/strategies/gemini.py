import uuid
from typing import List, Dict
from flexAgent.types.models import ToolCall, AgentResponse
from .base import LLMStrategy

class GeminiLLMStrategy(LLMStrategy):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0):
        from langchain_google_genai import ChatGoogleGenerativeAI
        self.api_key = api_key
        self.model_name = model
        self.temperature = temperature
        self._model = None
        self._tools = []

    def bind_tools(self, tools: List) -> "GeminiLLMStrategy":
        from langchain_google_genai import ChatGoogleGenerativeAI
        self._model = ChatGoogleGenerativeAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature,
            mode="json"
        ).bind_tools(tools)
        self._tools = tools
        return self

    def invoke(self, messages: List[Dict], tools: List = None) -> AgentResponse:
        if not self._model:
            self.bind_tools(tools or [])

        response = self._model.invoke(messages)

        tool_calls = []
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.get("id", str(uuid.uuid4())),
                    name=tc["name"],
                    args=tc["args"]
                ))

        return AgentResponse(
            content=response.content,
            tool_calls=tool_calls
        )
