"""
Unit Tests for LangChain & LangGraph Model Adapters.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.adapters import LangChainAdapter, LangGraphAdapter, MockAdapter


@pytest.mark.asyncio
async def test_langchain_adapter_stub():
    adapter = LangChainAdapter(model_name="gpt-4o")
    resp = await adapter.complete(messages=[{"role": "user", "content": "Hello LangChain"}])
    assert "LangChain Adapter Stub Response" in resp.content
    assert resp.model_name == "gpt-4o"


@pytest.mark.asyncio
async def test_langgraph_adapter_workflow():
    adapter = LangGraphAdapter(session_id="test-sess", goal="Test LangGraph Workflow")
    state = await adapter.run()
    assert state["session_id"] == "test-sess"
    assert state["status"] == "executed"


@pytest.mark.asyncio
async def test_mock_adapter_complete():
    adapter = MockAdapter()
    resp = await adapter.complete(messages=[{"role": "user", "content": "Hello"}])
    assert resp.content == "Mock execution completed successfully."
    assert resp.model_name == "mock-model"
