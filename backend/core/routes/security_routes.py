"""
Security Audit & Credential Redaction REST API Router.
Member 2 — Backend Core & Model Adapter Lead
"""

from typing import List, Dict, Any
from fastapi import APIRouter, status, HTTPException

from backend.core.schemas.security import (
    SecurityAuditReport,
    SanitizeRequest,
    SanitizeResponse,
    LeakDetail,
)
from backend.core.security import CredentialSanitizer, SecurityAuditor
from backend.core.routes.memory_routes import _memory_store
from backend.core.routes.trace_routes import _trace_store
from backend.core.config import settings

router = APIRouter()


@router.get(
    "/security/audit",
    response_model=SecurityAuditReport,
    status_code=status.HTTP_200_OK,
    summary="Perform Security Audit",
    description="Scan backend core memory stores, event trace logs, and system environment configurations to verify zero credential or key leaks.",
)
async def perform_security_audit() -> SecurityAuditReport:
    """Execute complete security audit scan across memory store, traces, and system settings."""
    extra_sources = {
        "CORS_ORIGINS": settings.CORS_ORIGINS,
        "DEFAULT_MODEL": settings.DEFAULT_MODEL,
        "FALLBACK_MODEL": settings.FALLBACK_MODEL,
    }
    report = SecurityAuditor.run_full_audit(
        memory_items=_memory_store,
        trace_logs=_trace_store,
        extra_sources=extra_sources,
    )
    return report


@router.post(
    "/security/sanitize",
    response_model=SanitizeResponse,
    status_code=status.HTTP_200_OK,
    summary="Sanitize Payload or Text",
    description="Scrub API keys (OpenAI, Anthropic, GitHub), passwords, bearer tokens, and private keys from input text or dictionary payload.",
)
async def sanitize_input(request: SanitizeRequest) -> SanitizeResponse:
    """Sanitize string or dictionary payload, masking sensitive API credentials."""
    sanitized_text = None
    sanitized_payload = None
    total_redacted = 0

    if request.text:
        sanitized_text, count = CredentialSanitizer.sanitize_text(request.text)
        total_redacted += count

    if request.payload:
        sanitized_payload, count = CredentialSanitizer.sanitize_payload(request.payload)
        total_redacted += count

    return SanitizeResponse(
        original_has_leaks=total_redacted > 0,
        redacted_count=total_redacted,
        sanitized_text=sanitized_text,
        sanitized_payload=sanitized_payload,
    )


@router.post(
    "/security/audit-text",
    response_model=List[LeakDetail],
    status_code=status.HTTP_200_OK,
    summary="Audit Raw Text Block",
    description="Scan a single text block and return granular list of any detected credential leak patterns.",
)
async def audit_text_block(text: str) -> List[LeakDetail]:
    """Scan raw text for exposed security credentials."""
    return SecurityAuditor.audit_text(text, source_label="UserTextInput")
