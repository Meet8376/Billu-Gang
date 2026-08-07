"""
Offline Mock Adapter for Zero-Cost Testing.
Member 2 — Backend Core & Model Adapter Lead
"""

import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from backend.core.adapters.base import ModelAdapter, CompletionResponse, ToolCallData


class MockAdapter(ModelAdapter):
    """Offline Mock ModelAdapter returning configurable responses for zero-cost testing."""

    def __init__(
        self,
        model_name: str = "mock-model",
        api_key: Optional[str] = None,
        preset_response: str = "Mock execution completed successfully.",
        mock_tool_calls: Optional[List[ToolCallData]] = None
    ):
        super().__init__(model_name=model_name, api_key=api_key)
        self.preset_response = preset_response
        self.mock_tool_calls = mock_tool_calls or []

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> CompletionResponse:
        """Return preset mock completion response."""
        tool_calls = self.mock_tool_calls
        if not tool_calls and tools:
            first_tool = tools[0]
            tool_name = first_tool.get("name", "mock_tool")
            tool_calls = [ToolCallData(id="mock_call_1", name=tool_name, args={"test": True})]

        in_tokens = self.get_token_count(str(messages))
        out_tokens = self.get_token_count(self.preset_response)

        return CompletionResponse(
            content=self.preset_response,
            tool_calls=tool_calls,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            total_tokens=in_tokens + out_tokens,
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
        """Stream mock response chunks with tiny delays."""
        words = self.preset_response.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.01)

    def get_token_count(self, text: str) -> int:
        """Return token count based on word count."""
        if not text:
            return 0
        return max(1, len(text.split()))
