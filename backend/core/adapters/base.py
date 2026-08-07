"""
Abstract Base Class ModelAdapter Interface with LangChain Integration.
Member 2 — Backend Core & Model Adapter Lead
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage


class CompletionResponse(BaseModel):
    """Model completion response representation."""
    content: str
    tool_calls: List[Dict[str, Any]] = []
    input_tokens: int = 0
    output_tokens: int = 0
    model_name: str = ""
    finish_reason: str = "stop"
    raw_message: Optional[Any] = None


class ModelAdapter(ABC):
    """Abstract Base Class for pluggable Model Adapters."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> CompletionResponse:
        """Generate a complete response using LangChain Runnable pipeline."""
        pass

    @abstractmethod
    async def stream_complete(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks live from LangChain runnable stream."""
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """Calculate token count for given text."""
        pass

    def _convert_to_langchain_messages(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> List[BaseMessage]:
        """Convert dictionary message list to standard LangChain BaseMessage objects."""
        langchain_msgs: List[BaseMessage] = []
        if system_prompt:
            langchain_msgs.append(SystemMessage(content=system_prompt))
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                langchain_msgs.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_msgs.append(AIMessage(content=content))
            else:
                langchain_msgs.append(HumanMessage(content=content))
        return langchain_msgs
