"""
Automatic Provider Fallback Manager (LangChain & LangGraph Compatible).
Member 2 — Backend Core & Model Adapter Lead
"""

import uuid
from typing import List, Dict, Any, Optional
from backend.core.adapters.base import ModelAdapter, CompletionResponse
from backend.core.schemas.sse_events import SSEEvent, EventType
from backend.core.routes.sse_routes import broadcaster


class FallbackAdapterManager:
    """Manages primary and fallback model adapters with automatic failover on rate-limits/outages."""

    def __init__(self, primary_adapter: ModelAdapter, fallback_adapters: List[ModelAdapter]):
        self.primary_adapter = primary_adapter
        self.fallback_adapters = fallback_adapters
        self.last_used_adapter: Optional[ModelAdapter] = None
        self.failover_history: List[Dict[str, Any]] = []

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
        last_exception: Optional[Exception] = None

        for index, adapter in enumerate(adapters):
            try:
                response = await adapter.complete(
                    messages=messages,
                    system_prompt=system_prompt,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                self.last_used_adapter = adapter
                return response
            except Exception as e:
                last_exception = e
                failover_record = {
                    "failed_adapter": adapter.model_name,
                    "attempt": index + 1,
                    "error": str(e),
                }
                self.failover_history.append(failover_record)

                # Broadcast error and failover SSE notification
                err_evt = SSEEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.ERROR_OCCURRED,
                    payload={
                        "failed_model": adapter.model_name,
                        "error_message": str(e),
                        "fallback_triggered": True,
                    }
                )
                await broadcaster.publish(err_evt)
                continue

        raise RuntimeError(
            f"All model adapters ({len(adapters)}) failed. Last error: {last_exception}"
        )
