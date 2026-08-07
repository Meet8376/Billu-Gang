"""
Phase 5 Unit Tests for Model Independence Verification & Financial Cost/Latency Reporting.
Member 2 — Backend Core & Model Adapter Lead
"""

import pytest
from backend.core.adapters import LangChainAdapter, MockAdapter
from backend.core.tracking import CostTracker
from backend.core.schemas.session import ModelBenchmarkMetrics

pytestmark = pytest.mark.asyncio


async def test_zero_harness_change_model_swap():
    """Verify that adapters can be swapped seamlessly with identical invocation interfaces."""
    adapters = [
        LangChainAdapter(model_name="gpt-4o"),
        MockAdapter(model_name="mock-model"),
    ]

    for adapter in adapters:
        resp = await adapter.complete(messages=[{"role": "user", "content": "Benchmark prompt"}])
        assert resp.content is not None
        assert resp.model_name in ["gpt-4o", "mock-model"]
        assert resp.input_tokens >= 0
        assert resp.output_tokens >= 0


def test_financial_summary_report_generation():
    """Verify latency and financial cost summary calculation."""
    tracker = CostTracker(max_budget_usd=5.0)
    tracker.add_usage(model="gpt-4o", input_tokens=4000, output_tokens=1000, latency_seconds=1.2)
    tracker.add_usage(model="gpt-4o-mini", input_tokens=2000, output_tokens=500, latency_seconds=0.4)

    report = tracker.generate_financial_summary_report(session_id="sess_report_test")
    assert report.session_id == "sess_report_test"
    assert report.total_input_tokens == 6000
    assert report.total_output_tokens == 1500
    assert report.total_tokens == 7500
    assert report.total_latency_seconds == pytest.approx(1.6, rel=1e-3)
    assert report.total_cost_usd > 0.0
    assert "gpt-4o" in report.per_model_breakdown
    assert "gpt-4o-mini" in report.per_model_breakdown
