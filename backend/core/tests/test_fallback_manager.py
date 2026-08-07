"""
Unit Tests for Model Adapter Fallback Manager.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.adapters import MockAdapter, FallbackAdapterManager


@pytest.mark.asyncio
async def test_fallback_manager_success():
    primary = MockAdapter(model_name="primary-mock")
    fallback = MockAdapter(model_name="fallback-mock")
    manager = FallbackAdapterManager(primary_adapter=primary, fallback_adapters=[fallback])

    resp = await manager.complete_with_fallback(messages=[{"role": "user", "content": "Hello"}])
    assert resp.model_name == "primary-mock"
