"""
Offline Mock Adapter for Zero-Cost Testing.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import AsyncGenerator, Dict, Any, List, Optional
from backend.core.adapters.base import ModelAdapter, CompletionResponse


class MockAdapter(ModelAdapter):
    """Offline Mock ModelAdapter returning static responses for zero-cost testing."""

    def __init__(self, model_name: str = "mock-model", api_key: Optional[str] = None):
        super().__init__(model_name=model_name, api_key=api_key)
        self.preset_response: str = "Mock execution completed successfully."

    async def complete(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> CompletionResponse:
        """Return preset mock completion response."""
        return CompletionResponse(
            content=self.preset_response,
            tool_calls=[],
            input_tokens=5,
            output_tokens=10,
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
        """Stream mock response chunks."""
        for word in self.preset_response.split():
            yield word + " "

    def get_token_count(self, text: str) -> int:
        """Return token count based on word count."""
        return len(text.split())
