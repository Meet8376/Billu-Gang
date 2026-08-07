"""Sandboxed Command Execution Service (Member 4 Lead).

Provides a secure tool execution layer wrapping DockerSandbox and ApprovalGate
to run shell commands safely inside containers.
"""

import logging
import time
from typing import Dict, Optional
from pydantic import BaseModel
from backend.orchestrator.sandbox.docker_manager import CommandResult, DockerSandbox
from backend.orchestrator.security.approval_gate import ApprovalGate, SafetyLevel
from backend.orchestrator.security.secret_redactor import redact_secrets

logger = logging.getLogger(__name__)


class ExecutionResponse(BaseModel):
    """Structured response for sandboxed tool command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_sec: float
    safety_level: str
    approved: bool
    timed_out: bool = False


class ContainerExecService:
    """Service wrapping Docker Sandbox execution with security approval checks."""

    def __init__(self, sandbox: DockerSandbox, approval_gate: Optional[ApprovalGate] = None):
        self.sandbox = sandbox
        self.approval_gate = approval_gate or ApprovalGate()

    async def execute_command(
        self,
        command: str,
        timeout_sec: int = 60,
        cwd: Optional[str] = None
    ) -> ExecutionResponse:
        """Evaluates command safety and executes inside Docker container if approved."""
        start_time = time.time()

        # Step 1: Security Safety Evaluation
        safety_result = self.approval_gate.evaluate_command(command)

        # Step 2: Approval Gate Handling
        if safety_result.safety_level == SafetyLevel.REQUIRES_APPROVAL:
            approved = await self.approval_gate.check_approval(command)
            if not approved:
                logger.warning(f"Command execution rejected by approval gate: {command}")
                return ExecutionResponse(
                    command=redact_secrets(command),
                    exit_code=126,  # Command invoked cannot execute
                    stdout="",
                    stderr=f"Command execution rejected by safety approval gate: {safety_result.reason}",
                    duration_sec=time.time() - start_time,
                    safety_level=safety_result.safety_level.value,
                    approved=False,
                    timed_out=False
                )
        elif safety_result.safety_level == SafetyLevel.BLOCKED:
            return ExecutionResponse(
                command=redact_secrets(command),
                exit_code=126,
                stdout="",
                stderr=f"Command blocked by security policy: {safety_result.reason}",
                duration_sec=time.time() - start_time,
                safety_level=safety_result.safety_level.value,
                approved=False,
                timed_out=False
            )

        # Step 3: Execute in Sandbox Container
        if not self.sandbox.is_running():
            self.sandbox.start()

        cmd_res: CommandResult = self.sandbox.exec_command(command, timeout_sec=timeout_sec, cwd=cwd)

        return ExecutionResponse(
            command=redact_secrets(command),
            exit_code=cmd_res.exit_code,
            stdout=redact_secrets(cmd_res.stdout),
            stderr=redact_secrets(cmd_res.stderr),
            duration_sec=cmd_res.duration_sec,
            safety_level=safety_result.safety_level.value,
            approved=True,
            timed_out=cmd_res.timed_out
        )
