"""
Phase 2 Unit Tests for LangChain, LangGraph & Mock Adapters.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.adapters import LangChainAdapter, LangGraphAdapter, GeminiAdapter, MockAdapter, ToolCallData

pytestmark = pytest.mark.asyncio



async def test_langchain_adapter_completion_stub():
    adapter = LangChainAdapter(model_name="gpt-4o")
    resp = await adapter.complete(
        messages=[{"role": "user", "content": "Analyze repository architecture"}],
        tools=[{"name": "read_file", "description": "Read file contents"}]
    )
    assert "[LangChain Execution Complete" in resp.content
    assert resp.model_name == "gpt-4o"
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "read_file"


async def test_langchain_adapter_streaming():
    adapter = LangChainAdapter(model_name="gpt-4o")
    chunks = []
    async for chunk in adapter.stream_complete(messages=[{"role": "user", "content": "Stream test"}]):
        chunks.append(chunk)
    assert len(chunks) > 0


async def test_langgraph_adapter_full_workflow():
    adapter = LangGraphAdapter(session_id="sess_phase2_test", goal="Refactor backend core adapters")
    state = await adapter.run()
    assert state["session_id"] == "sess_phase2_test"
    assert state["status"] == "verified"
    assert len(state["task_dag"]) == 2
    assert "Patch successfully applied" in state["output"]
    assert len(state["logs"]) == 3


async def test_mock_adapter_custom_tool_calls():
    custom_calls = [ToolCallData(id="c1", name="search_code", args={"query": "def main"})]
    adapter = MockAdapter(preset_response="Mocked completion", mock_tool_calls=custom_calls)
    resp = await adapter.complete(messages=[{"role": "user", "content": "Find main"}])
    assert resp.content == "Mocked completion"
    assert resp.tool_calls[0].name == "search_code"


async def test_gemini_adapter_integration():
    adapter = GeminiAdapter(model_name="gemini-1.5-pro")
    resp = await adapter.complete(messages=[{"role": "user", "content": "Test Gemini adapter integration"}])
    assert resp.model_name == "gemini-1.5-pro"
    assert resp.content is not None

