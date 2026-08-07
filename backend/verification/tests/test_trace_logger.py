"""
Phase 1 Unit Tests for JSONL Trace Schema & TraceLogger Engine.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
import pytest
from backend.verification.trace.trace_schema import TraceEvent, TraceEventType
from backend.verification.trace.trace_logger import TraceLogger

pytestmark = pytest.mark.asyncio


def test_trace_event_jsonl_serialization():
    event = TraceEvent(
        session_id="sess_p1_001",
        event_type=TraceEventType.PLAN_REVISED,
        actor="orchestrator",
        payload={"plan_nodes": 5},
        token_cost_usd=0.005,
        duration_ms=120.5,
    )
    line = event.to_jsonl_line()
    assert line.endswith("\n")
    assert '"event_type":"plan_revised"' in line

    parsed = TraceEvent.from_jsonl_line(line)
    assert parsed.session_id == "sess_p1_001"
    assert parsed.event_type == TraceEventType.PLAN_REVISED
    assert parsed.token_cost_usd == 0.005


def test_trace_logger_file_append_and_read(tmp_path):
    log_file = tmp_path / "test_trace.jsonl"
    logger = TraceLogger(log_filepath=str(log_file))

    evt1 = logger.log_event(
        session_id="sess_p1_002",
        event_type=TraceEventType.TOOL_CALLED,
        payload={"tool_name": "read_file"},
    )
    evt2 = logger.log_event(
        session_id="sess_p1_002",
        event_type=TraceEventType.TEST_RUN_COMPLETED,
        payload={"passed": True, "coverage": 95.0},
    )

    assert log_file.exists()
    events = logger.read_traces(session_id="sess_p1_002")
    assert len(events) == 2
    assert events[0].payload["tool_name"] == "read_file"
    assert events[1].event_type == TraceEventType.TEST_RUN_COMPLETED


def test_trace_logger_filtering(tmp_path):
    log_file = tmp_path / "filtered_trace.jsonl"
    logger = TraceLogger(log_filepath=str(log_file))

    logger.log_event("sess_A", TraceEventType.PLAN_REVISED, {"node": 1})
    logger.log_event("sess_B", TraceEventType.TOOL_CALLED, {"node": 2})
    logger.log_event("sess_A", TraceEventType.TOOL_CALLED, {"node": 3})

    sess_a_events = logger.read_traces(session_id="sess_A")
    assert len(sess_a_events) == 2

    tool_events = logger.read_traces(event_type=TraceEventType.TOOL_CALLED)
    assert len(tool_events) == 2


async def test_trace_logger_async(tmp_path):
    log_file = tmp_path / "async_trace.jsonl"
    logger = TraceLogger(log_filepath=str(log_file))

    evt = await logger.log_event_async(
        session_id="sess_async",
        event_type=TraceEventType.VERIFICATION_STEP,
        payload={"step": "lint_check"},
    )
    assert evt.session_id == "sess_async"

    traces = logger.read_traces(session_id="sess_async")
    assert len(traces) == 1
    assert traces[0].payload["step"] == "lint_check"


def test_trace_logger_clear(tmp_path):
    log_file = tmp_path / "clear_trace.jsonl"
    logger = TraceLogger(log_filepath=str(log_file))

    logger.log_event("sess_clear", TraceEventType.ERROR_OCCURRED, {"err": "timeout"})
    assert len(logger.read_traces()) == 1

    logger.clear_traces()
    assert len(logger.read_traces()) == 0
