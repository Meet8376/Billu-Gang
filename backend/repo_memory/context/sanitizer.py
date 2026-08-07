"""
Prompt & Secret Sanitizer (FR17)

Strips potential prompt injections, credential keys, passwords,
and sensitive tokens from external issue descriptions, user queries, and code snippets.
"""

import re
from typing import List, Dict, Tuple, Optional


class Sanitizer:
    """
    Sanitizer for detecting and redacting secrets, credentials, and prompt injections.
    """

    # Secret credential patterns (API keys, tokens, private keys)
    SECRET_PATTERNS: List[Tuple[str, re.Pattern]] = [
        ("OpenAI API Key", re.compile(r"sk-[a-zA-Z0-9]{32,64}")),
        ("GitHub Personal Access Token", re.compile(r"ghp_[a-zA-Z0-9]{36}")),
        ("GitHub OAuth Token", re.compile(r"gho_[a-zA-Z0-9]{36}")),
        ("AWS Access Key ID", re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}")),
        ("AWS Secret Key", re.compile(r"(?i)aws_secret_access_key\s*=\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?")),
        ("RSA/PEM Private Key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
        ("Generic Password Assignment", re.compile(r"(?i)(?:password|passwd|pwd|secret)\s*[:=]\s*['\"]([^'\"]{6,})['\"]")),
        ("Generic Bearer Token", re.compile(r"Bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*")),
    ]

    # Common prompt injection patterns
    INJECTION_PATTERNS: List[Tuple[str, re.Pattern]] = [
        ("System Prompt Override", re.compile(r"(?i)ignore (?:all )?(?:previous|above) instructions")),
        ("Disregard Rules", re.compile(r"(?i)disregard (?:all )?(?:prior|previous) (?:prompts|rules|instructions)")),
        ("System Persona Hijack", re.compile(r"(?i)you are now (?:unrestricted|DAN|a helpful assistant without rules)")),
        ("System Tag Injection", re.compile(r"<\/system>|<system>|\[SYSTEM PROMPT\]")),
    ]

    def __init__(self, redact_secrets: bool = True, neutralize_injections: bool = True):
        self.redact_secrets = redact_secrets
        self.neutralize_injections = neutralize_injections

    def sanitize(self, text: str) -> str:
        """
        Sanitize prompt text by redacting secret credentials and neutralizing injection attempts.

        Args:
            text: Input string to sanitize

        Returns:
            Sanitized string
        """
        if not text:
            return text

        result = text

        if self.redact_secrets:
            result = self.redact_credentials(result)

        if self.neutralize_injections:
            result = self.neutralize_prompt_injections(result)

        return result

    def redact_credentials(self, text: str) -> str:
        """Redact detected API keys, passwords, and tokens"""
        sanitized = text
        for label, pattern in self.SECRET_PATTERNS:
            sanitized = pattern.sub(f"[REDACTED_{label.upper().replace(' ', '_')}]", sanitized)
        return sanitized

    def neutralize_prompt_injections(self, text: str) -> str:
        """Neutralize prompt injection attempts"""
        sanitized = text
        for label, pattern in self.INJECTION_PATTERNS:
            sanitized = pattern.sub(f"[NEUTRALIZED_INJECTION_{label.upper().replace(' ', '_')}]", sanitized)
        return sanitized


def sanitize_prompt_text(text: str) -> str:
    """
    Convenience function to sanitize text.

    Args:
        text: Input string

    Returns:
        Sanitized string
    """
    sanitizer = Sanitizer()
    return sanitizer.sanitize(text)
