"""
Automatic Provider Fallback Manager.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import List, Dict, Any, Optional
from backend.core.adapters.base import ModelAdapter, CompletionResponse


class FallbackAdapterManager:
    """Manages primary and fallback model adapters with automatic failover on rate-limits/outages."""

    def __init__(self, primary_adapter: ModelAdapter, fallback_adapters: List[ModelAdapter]):
        self.primary_adapter = primary_adapter
        self.fallback_adapters = fallback_adapters

    async def complete_with_fallback(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> CompletionResponse:
        """Attempt completion on primary adapter, falling back to backups on error."""
        adapters = [self.primary_adapter] + self.fallback_adapters
        last_exception = None

        for adapter in adapters:
            try:
                return await adapter.complete(
                    messages=messages,
                    system_prompt=system_prompt,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as e:
                last_exception = e
                continue

        raise RuntimeError(f"All model adapters failed. Last error: {last_exception}")
