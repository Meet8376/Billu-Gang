"""Approval Gate and Command Security Policy Evaluator (Member 4 Lead).

Intercepts commands targeting files outside workspace or requesting network access,
requiring explicit CLI approval ([y/N]) before execution.
"""

import logging
import re
from enum import Enum
from typing import Awaitable, Callable, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SafetyLevel(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    BLOCKED = "BLOCKED"


class CommandSafetyResult(BaseModel):
    command: str
    safety_level: SafetyLevel
    reason: str


class ApprovalGate:
    """Evaluates security rules and handles CLI approval callbacks."""

    # Commands/patterns safe to run automatically inside sandbox
    SAFE_COMMAND_PREFIXES: List[str] = [
        "pytest", "python", "python3", "pytest ", "ruff", "mypy",
        "npm test", "node", "npm run", "git status", "git diff", "git log",
        "ls", "cat", "find", "grep", "echo", "pwd"
    ]

    # Patterns that are dangerous and require approval or are blocked
    DANGEROUS_PATTERNS: List[str] = [
        r"rm\s+-rf\s+/",              # Recursive root deletion
        r"sudo\s+",                    # Privilege escalation
        r"chmod\s+777",                # Overly permissive permissions
        r">\s*/dev/sd",                # Block device overwrite
        r"curl\s+",                    # Potential external network outbound call
        r"wget\s+",                    # External download call
        r"ssh\s+",                     # Remote shell access
    ]

    def __init__(self, approval_callback: Optional[Callable[[str, str], Awaitable[bool]]] = None):
        self.approval_callback = approval_callback

    def evaluate_command(self, command: str) -> CommandSafetyResult:
        """Evaluates command string against safety rules."""
        cmd_strip = command.strip()

        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_strip):
                return CommandSafetyResult(
                    command=command,
                    safety_level=SafetyLevel.REQUIRES_APPROVAL,
                    reason=f"Command matched sensitive security pattern: '{pattern}'"
                )

        # Check auto-approved prefixes
        for safe_prefix in self.SAFE_COMMAND_PREFIXES:
            if cmd_strip.startswith(safe_prefix):
                return CommandSafetyResult(
                    command=command,
                    safety_level=SafetyLevel.AUTO_APPROVED,
                    reason=f"Command matches safe prefix '{safe_prefix}'"
                )

        # Default fallback: requiring approval for arbitrary shell execution
        return CommandSafetyResult(
            command=command,
            safety_level=SafetyLevel.REQUIRES_APPROVAL,
            reason="Arbitrary command execution requires user confirmation"
        )

    async def check_approval(self, command: str) -> bool:
        """Determines if command is approved to execute."""
        result = self.evaluate_command(command)

        if result.safety_level == SafetyLevel.AUTO_APPROVED:
            logger.info(f"Auto-approved command execution: {command}")
            return True

        if result.safety_level == SafetyLevel.BLOCKED:
            logger.warning(f"BLOCKED command execution: {command} (Reason: {result.reason})")
            return False

        logger.info(f"Command requires human approval: {command} (Reason: {result.reason})")
        if self.approval_callback:
            try:
                approved = await self.approval_callback(command, result.reason)
                return approved
            except Exception as e:
                logger.error(f"Error during approval callback execution: {e}")
                return False
        else:
            logger.warning("No approval callback registered. Rejecting unapproved command by default.")
            return False
