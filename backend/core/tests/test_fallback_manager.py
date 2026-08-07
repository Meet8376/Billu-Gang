"""
Phase 4 Unit Tests for Model Adapter Fallback Manager & Failover Logic.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.adapters import MockAdapter, FallbackAdapterManager
from backend.core.adapters.base import ModelAdapter, CompletionResponse

pytestmark = pytest.mark.asyncio


class FailingAdapter(ModelAdapter):
    """Failing Adapter simulating API rate limits or provider outages."""

    async def complete(self, messages, system_prompt=None, tools=None, temperature=0.2, max_tokens=4096):
        raise RuntimeError("API Rate Limit Exceeded (Simulated Provider Outage)")

    async def stream_complete(self, messages, system_prompt=None, tools=None, temperature=0.2, max_tokens=4096):
        raise RuntimeError("API Rate Limit Exceeded")

    def get_token_count(self, text: str) -> int:
        return len(text) // 4


async def test_fallback_manager_primary_success():
    primary = MockAdapter(model_name="primary-mock")
    fallback = MockAdapter(model_name="fallback-mock")
    manager = FallbackAdapterManager(primary_adapter=primary, fallback_adapters=[fallback])

    resp = await manager.complete_with_fallback(messages=[{"role": "user", "content": "Hello"}])
    assert resp.model_name == "primary-mock"


async def test_fallback_manager_failover_to_secondary():
    failing_primary = FailingAdapter(model_name="primary-failing")
    successful_fallback = MockAdapter(model_name="fallback-success")
    manager = FallbackAdapterManager(
        primary_adapter=failing_primary,
        fallback_adapters=[successful_fallback]
    )

    resp = await manager.complete_with_fallback(messages=[{"role": "user", "content": "Test Failover"}])
    assert resp.model_name == "fallback-success"
    assert len(manager.failover_history) == 1
    assert manager.failover_history[0]["failed_adapter"] == "primary-failing"


async def test_fallback_manager_all_adapters_fail():
    failing1 = FailingAdapter(model_name="failing-1")
    failing2 = FailingAdapter(model_name="failing-2")
    manager = FallbackAdapterManager(primary_adapter=failing1, fallback_adapters=[failing2])

    with pytest.raises(RuntimeError) as exc_info:
        await manager.complete_with_fallback(messages=[{"role": "user", "content": "Test Total Failure"}])

    assert "All model adapters (2) failed" in str(exc_info.value)
