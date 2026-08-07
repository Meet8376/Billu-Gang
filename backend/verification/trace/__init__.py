"""
Structured Event Tracing & OpenTelemetry Package.
Member 5 — Verification, Benchmarking & Evaluation Lead
"""

from backend.verification.trace.trace_schema import TraceEvent, TraceEventType
from backend.verification.trace.trace_logger import TraceLogger

__all__ = ["TraceEvent", "TraceEventType", "TraceLogger"]
