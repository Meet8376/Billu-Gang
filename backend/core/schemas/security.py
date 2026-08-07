"""
Security Audit & Credential Redaction Pydantic Schemas.
Member 2 — Backend Core & Model Adapter Lead
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LeakDetail(BaseModel):
    """Details of a detected security credential leak."""
    field_or_source: str = Field(..., description="Location, field, or source where leak was detected")
    leak_type: str = Field(..., description="Type of key or secret detected (e.g., OpenAI API Key, Anthropic API Key)")
    redacted_preview: str = Field(..., description="Redacted pattern preview")


class SecurityAuditReport(BaseModel):
    """Complete Security Audit Summary Report for Backend Core."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when security audit was executed")
    clean: bool = Field(..., description="True if zero security leaks detected")
    total_items_scanned: int = Field(..., description="Total memory items, logs, traces, and settings scanned")
    leaks_detected_count: int = Field(..., description="Total number of potential leaks detected")
    redacted_count: int = Field(..., description="Total number of secrets auto-redacted")
    leak_details: List[LeakDetail] = Field(default_factory=list, description="List of detected leak details")
    audit_summary: str = Field(..., description="Human-readable summary of the security audit")


class SanitizeRequest(BaseModel):
    """Request payload for text/object credential sanitization."""
    text: Optional[str] = Field(None, description="Text string to sanitize")
    payload: Optional[Dict[str, Any]] = Field(None, description="Structured payload dictionary to sanitize")


class SanitizeResponse(BaseModel):
    """Sanitizer response containing scrubbed result."""
    original_has_leaks: bool = Field(..., description="True if credentials were found and scrubbed")
    redacted_count: int = Field(..., description="Number of sensitive fields or keys scrubbed")
    sanitized_text: Optional[str] = Field(None, description="Sanitized text output")
    sanitized_payload: Optional[Dict[str, Any]] = Field(None, description="Sanitized dictionary payload")
