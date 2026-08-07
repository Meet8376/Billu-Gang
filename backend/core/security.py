"""
Credential Sanitization, Redaction & Security Audit Engine.
Member 2 — Backend Core & Model Adapter Lead
"""

import re
import copy
from typing import Any, Tuple, List, Dict, Union
from datetime import datetime

from backend.core.schemas.security import (
    LeakDetail,
    SecurityAuditReport,
    SanitizeResponse,
)


class CredentialSanitizer:
    """Regex pattern matcher and deep-redactor for credentials and sensitive tokens."""

    # High-precision regular expressions for credentials and API keys
    PATTERNS: List[Tuple[str, str, str]] = [
        (
            "Anthropic API Key",
            r"\bsk-ant-(?:api\d*-)?[a-zA-Z0-9_\-]{20,}\b",
            "[REDACTED_ANTHROPIC_KEY]",
        ),
        (
            "OpenAI API Key",
            r"\bsk-(?:proj-|svcacct-|)[a-zA-Z0-9_\-]{20,}\b",
            "[REDACTED_OPENAI_KEY]",
        ),

        (
            "GitHub Personal Access Token",
            r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b",
            "[REDACTED_GITHUB_TOKEN]",
        ),
        (
            "GitHub Fine-Grained Token",
            r"\bgithub_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}\b",
            "[REDACTED_GITHUB_PAT]",
        ),
        (
            "Private Key Block",
            r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----[\s\S]*?-----END (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
            "[REDACTED_PRIVATE_KEY]",
        ),
        (
            "Database Connection Credentials",
            r"(?i)\b(postgres|postgresql|mysql|mongodb|redis):\/\/([^:]+):([^@]+)@",
            r"\1://\2:[REDACTED_DB_PASS]@",
        ),
        (
            "Bearer Authorization Token",
            r"(?i)\bBearer\s+[a-zA-Z0-9\-\._~\+\/]{16,}=*",
            "Bearer [REDACTED_BEARER_TOKEN]",
        ),
    ]

    # Sensitive dictionary key names to automatically redact if values look like credentials
    SENSITIVE_KEY_NAMES = {
        "api_key",
        "apikey",
        "secret",
        "secret_key",
        "password",
        "passwd",
        "auth_token",
        "access_token",
        "private_key",
        "credentials",
    }

    @classmethod
    def sanitize_text(cls, text: str) -> Tuple[str, int]:
        """Sanitize a text string by masking detected API keys and secrets."""
        if not text or not isinstance(text, str):
            return text, 0

        sanitized = text
        redacted_count = 0

        for leak_type, pattern, replacement in cls.PATTERNS:
            matches = list(re.finditer(pattern, sanitized))
            if matches:
                redacted_count += len(matches)
                sanitized = re.sub(pattern, replacement, sanitized)

        return sanitized, redacted_count

    @classmethod
    def sanitize_payload(cls, data: Any) -> Tuple[Any, int]:
        """Recursively sanitize dicts, lists, strings, and objects."""
        if isinstance(data, str):
            return cls.sanitize_text(data)

        if isinstance(data, dict):
            total_redacted = 0
            sanitized_dict = {}
            for k, v in data.items():
                # Check if key name implies sensitive content
                if isinstance(k, str) and k.lower() in cls.SENSITIVE_KEY_NAMES:
                    if isinstance(v, str) and not v.startswith("[REDACTED"):
                        sanitized_dict[k] = f"[REDACTED_{k.upper()}]"
                        total_redacted += 1
                        continue

                sanitized_val, count = cls.sanitize_payload(v)
                sanitized_dict[k] = sanitized_val
                total_redacted += count
            return sanitized_dict, total_redacted

        if isinstance(data, list):
            total_redacted = 0
            sanitized_list = []
            for item in data:
                sanitized_item, count = cls.sanitize_payload(item)
                sanitized_list.append(sanitized_item)
                total_redacted += count
            return sanitized_list, total_redacted

        return data, 0


class SecurityAuditor:
    """Audits memory storage, trace logs, and system data for potential leaks."""

    @classmethod
    def audit_text(cls, text: str, source_label: str) -> List[LeakDetail]:
        """Audit a raw text string for potential credential leaks."""
        leaks: List[LeakDetail] = []
        if not text or not isinstance(text, str):
            return leaks

        for leak_type, pattern, _ in CredentialSanitizer.PATTERNS:
            matches = list(re.finditer(pattern, text))
            for m in matches:
                matched_str = m.group(0)
                preview = matched_str[:6] + "..." + matched_str[-4:] if len(matched_str) > 10 else "***"
                leaks.append(
                    LeakDetail(
                        field_or_source=source_label,
                        leak_type=leak_type,
                        redacted_preview=preview,
                    )
                )
        return leaks

    @classmethod
    def audit_object(cls, obj: Any, source_prefix: str) -> List[LeakDetail]:
        """Recursively audit an object or dict for leaks."""
        leaks: List[LeakDetail] = []
        if isinstance(obj, str):
            return cls.audit_text(obj, source_prefix)

        if isinstance(obj, dict):
            for k, v in obj.items():
                label = f"{source_prefix}.{k}"
                if isinstance(k, str) and k.lower() in CredentialSanitizer.SENSITIVE_KEY_NAMES:
                    if isinstance(v, str) and not v.startswith("[REDACTED"):
                        preview = v[:4] + "..." if len(v) > 4 else "***"
                        leaks.append(
                            LeakDetail(
                                field_or_source=label,
                                leak_type="Exposed Sensitive Key",
                                redacted_preview=preview,
                            )
                        )
                leaks.extend(cls.audit_object(v, label))

        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                leaks.extend(cls.audit_object(item, f"{source_prefix}[{idx}]"))

        elif hasattr(obj, "__dict__"):
            leaks.extend(cls.audit_object(obj.__dict__, source_prefix))

        return leaks

    @classmethod
    def run_full_audit(
        cls,
        memory_items: List[Any],
        trace_logs: List[Any],
        extra_sources: Dict[str, Any] = None,
    ) -> SecurityAuditReport:
        """Run a full security audit across memory store, trace logs, and system data."""
        all_leaks: List[LeakDetail] = []
        total_items_scanned = 0

        # 1. Audit Tiered Memory Store
        for idx, item in enumerate(memory_items):
            total_items_scanned += 1
            item_dict = item.model_dump() if hasattr(item, "model_dump") else item
            all_leaks.extend(cls.audit_object(item_dict, f"MemoryItem[{idx}]"))

        # 2. Audit Trace Event Logs
        for idx, log in enumerate(trace_logs):
            total_items_scanned += 1
            log_dict = log.model_dump() if hasattr(log, "model_dump") else log
            all_leaks.extend(cls.audit_object(log_dict, f"TraceLog[{idx}]"))

        # 3. Audit Extra Sources (e.g. system settings / config)
        if extra_sources:
            for source_name, source_data in extra_sources.items():
                total_items_scanned += 1
                all_leaks.extend(cls.audit_object(source_data, f"Config[{source_name}]"))

        is_clean = len(all_leaks) == 0
        summary = (
            "✅ SECURITY AUDIT PASSED: Zero API keys or local host credentials detected in backend core."
            if is_clean
            else f"⚠️ SECURITY AUDIT WARNING: {len(all_leaks)} potential credential leaks detected during security scan."
        )

        return SecurityAuditReport(
            timestamp=datetime.utcnow(),
            clean=is_clean,
            total_items_scanned=total_items_scanned,
            leaks_detected_count=len(all_leaks),
            redacted_count=len(all_leaks),
            leak_details=all_leaks,
            audit_summary=summary,
        )
