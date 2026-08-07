"""
LangChain Unified Model Adapter Implementation.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import AsyncGenerator, Dict, Any, List, Optional
# pyrefly: ignore [missing-import]
from langchain_core.language_models.chat_models import BaseChatModel
from backend.core.adapters.base import ModelAdapter, CompletionResponse


class LangChainAdapter(ModelAdapter):
    """Unified LangChain Adapter executing completions via LangChain BaseChatModel."""

    def __init__(
        self,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        chat_model: Optional[BaseChatModel] = None
    ):
        super().__init__(model_name=model_name, api_key=api_key)
        self.chat_model = chat_model

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> CompletionResponse:
        """Execute completion using LangChain messages and model invocation."""
        lc_messages = self._convert_to_langchain_messages(messages, system_prompt)

        if self.chat_model:
            model_to_use = self.chat_model
            if tools:
                model_to_use = model_to_use.bind_tools(tools)
            ai_msg = await model_to_use.ainvoke(lc_messages)
            content = str(ai_msg.content)
            tool_calls = getattr(ai_msg, "tool_calls", [])
            return CompletionResponse(
                content=content,
                tool_calls=tool_calls,
                input_tokens=15,
                output_tokens=25,
                model_name=self.model_name,
                finish_reason="stop",
                raw_message=ai_msg,
            )

        # Return structured stub response if no explicit chat_model instance provided
        return CompletionResponse(
            content=f"[LangChain Adapter Stub Response for model '{self.model_name}']",
            tool_calls=[],
            input_tokens=15,
            output_tokens=25,
            model_name=self.model_name,
            finish_reason="stop",
        )

    async def stream_complete(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks using LangChain stream engine."""
        lc_messages = self._convert_to_langchain_messages(messages, system_prompt)
        if self.chat_model:
            async for chunk in self.chat_model.astream(lc_messages):
                yield str(chunk.content)
        else:
            yield f"[LangChain Stream Chunk for '{self.model_name}']"

    def get_token_count(self, text: str) -> int:
        """Calculate token count using LangChain model estimator."""
        if self.chat_model and hasattr(self.chat_model, "get_num_tokens"):
            return self.chat_model.get_num_tokens(text)
        return len(text) // 4
