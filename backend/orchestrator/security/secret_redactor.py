"""Secret Redactor and Credential Scrubber (Member 4 Lead).

Redacts API keys, tokens, passwords, and environment secrets from stdout, stderr,
command strings, and trace event payloads before logging or sending to CLI.
"""

import re
from typing import List, Set


class SecretRedactor:
    """Scubs API keys, credentials, and tokens from text outputs."""

    # Common secret regex patterns (OpenAI, Anthropic, GitHub, AWS, JWT, Bearer tokens)
    DEFAULT_PATTERNS: List[re.Pattern] = [
        re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE),                      # OpenAI / Anthropic / Project API keys
        re.compile(r"ghp_[a-zA-Z0-9]{36}", re.IGNORECASE),                         # GitHub Personal Access Tokens
        re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),                           # AWS Access Key ID
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),             # Bearer Auth Tokens
        re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}", re.IGNORECASE), # JWT Tokens
        re.compile(r"(password|passwd|secret|api_key|token)\s*=\s*['\"]?([^'\"\s]+)['\"]?", re.IGNORECASE), # Config key=val
    ]

    def __init__(self):
        self.registered_secrets: Set[str] = set()

    def register_secret(self, secret: str) -> None:
        """Registers an explicit secret string (e.g. from environment) to scrub."""
        if secret and len(secret) > 3:
            self.registered_secrets.add(secret)

    def redact(self, text: str) -> str:
        """Replaces all identified secrets and registered tokens with [REDACTED_SECRET]."""
        if not text:
            return ""

        redacted_text = text

        # 1. Scrub registered explicit secrets first
        for secret in self.registered_secrets:
            redacted_text = redacted_text.replace(secret, "[REDACTED_SECRET]")

        # 2. Scrub pattern matches
        for pattern in self.DEFAULT_PATTERNS:
            # Handle key-value capture groups specially if present
            if pattern.groups == 2:
                redacted_text = pattern.sub(r"\1=[REDACTED_SECRET]", redacted_text)
            else:
                redacted_text = pattern.sub("[REDACTED_SECRET]", redacted_text)

        return redacted_text


# Global default instance helper
_global_redactor = SecretRedactor()


def redact_secrets(text: str) -> str:
    """Utility function to scrub secrets using global redactor."""
    return _global_redactor.redact(text)
