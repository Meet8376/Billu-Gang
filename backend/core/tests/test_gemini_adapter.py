"""
Unit Tests for Gemini Model Adapter & Gemini LangGraph Workflow Adapter.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.adapters import GeminiAdapter, GeminiLangGraphAdapter, FallbackAdapterManager, MockAdapter

pytestmark = pytest.mark.asyncio


async def test_gemini_adapter_initialization_defaults():
    adapter = GeminiAdapter()
    assert adapter.model_name == "gemini-1.5-pro"

    custom_adapter = GeminiAdapter(model_name="gemini-1.5-flash", api_key="test-key-123")
    assert custom_adapter.model_name == "gemini-1.5-flash"
    assert custom_adapter.api_key == "test-key-123"


async def test_gemini_adapter_completion():
    adapter = GeminiAdapter(model_name="gemini-1.5-pro")
    resp = await adapter.complete(
        messages=[{"role": "user", "content": "Analyze backend core architecture"}],
        tools=[{"name": "read_code", "description": "Read source code file"}]
    )
    assert resp.model_name == "gemini-1.5-pro"
    assert "[LangChain Execution Complete" in resp.content or resp.content != ""
    assert len(resp.tool_calls) >= 1
    assert resp.tool_calls[0].name == "read_code"


async def test_gemini_adapter_streaming():
    adapter = GeminiAdapter(model_name="gemini-1.5-pro")
    chunks = []
    async for chunk in adapter.stream_complete(messages=[{"role": "user", "content": "Hello Gemini"}]):
        chunks.append(chunk)
    assert len(chunks) > 0


async def test_gemini_adapter_token_counting():
    adapter = GeminiAdapter(model_name="gemini-1.5-pro")
    token_count = adapter.get_token_count("Hello world from Gemini adapter unit test!")
    assert token_count > 0


async def test_gemini_langgraph_adapter_workflow():
    adapter = GeminiLangGraphAdapter(
        session_id="sess_gemini_test",
        goal="Add Google Gemini support to model adapters",
        model_name="gemini-1.5-pro",
    )
    final_state = await adapter.run()
    assert final_state["session_id"] == "sess_gemini_test"
    assert final_state["status"] == "verified"
    assert len(final_state["task_dag"]) == 2
    assert "Gemini Patch successfully generated" in final_state["output"]
    assert len(final_state["logs"]) == 4


async def test_gemini_adapter_in_fallback_manager():
    gemini = GeminiAdapter(model_name="gemini-1.5-pro")
    mock_fallback = MockAdapter(preset_response="Failover mock response")
    fallback_mgr = FallbackAdapterManager(primary_adapter=gemini, fallback_adapters=[mock_fallback])

    resp = await fallback_mgr.complete_with_fallback(
        messages=[{"role": "user", "content": "Test failover execution"}]
    )
    assert resp.content is not None
    assert fallback_mgr.last_used_adapter is not None
