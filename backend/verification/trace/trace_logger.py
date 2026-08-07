"""
Async JSONL Event Tracer Engine.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from backend.verification.trace.trace_schema import TraceEvent, TraceEventType


class TraceLogger:
    """Async & sync JSONL event tracer for appending structured trace events to trace.jsonl."""

    def __init__(self, log_filepath: Optional[str] = None):
        if log_filepath:
            self.log_path = Path(log_filepath)
        else:
            self.log_path = Path(os.getcwd()) / "backend" / "verification" / "trace" / "trace.jsonl"

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._memory_buffer: List[TraceEvent] = []

    def log_event(
        self,
        session_id: str,
        event_type: TraceEventType,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "verification_runner",
        token_cost_usd: float = 0.0,
        duration_ms: float = 0.0,
    ) -> TraceEvent:
        """Create, append to trace.jsonl file, and return a TraceEvent."""
        event = TraceEvent(
            session_id=session_id,
            event_type=event_type,
            actor=actor,
            payload=payload or {},
            token_cost_usd=token_cost_usd,
            duration_ms=duration_ms,
        )

        line = event.to_jsonl_line()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)

        self._memory_buffer.append(event)
        return event

    async def log_event_async(
        self,
        session_id: str,
        event_type: TraceEventType,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "verification_runner",
        token_cost_usd: float = 0.0,
        duration_ms: float = 0.0,
    ) -> TraceEvent:
        """Asynchronously create and log a TraceEvent."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.log_event,
            session_id,
            event_type,
            payload,
            actor,
            token_cost_usd,
            duration_ms,
        )

    def read_traces(
        self,
        session_id: Optional[str] = None,
        event_type: Optional[TraceEventType] = None,
    ) -> List[TraceEvent]:
        """Read and parse trace events from trace.jsonl file."""
        if not self.log_path.exists():
            return []

        events: List[TraceEvent] = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    evt = TraceEvent.from_jsonl_line(line_str)
                    if session_id and evt.session_id != session_id:
                        continue
                    if event_type and evt.event_type != event_type:
                        continue
                    events.append(evt)
                except Exception:
                    continue
        return events

    def clear_traces(self) -> None:
        """Clear the log file and memory buffer."""
        self._memory_buffer.clear()
        if self.log_path.exists():
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("")
