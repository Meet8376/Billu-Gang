"""Unit tests for Member 4 Phase 1 Sandbox & Security components."""

import os
import unittest

try:
    import pytest
except ImportError:
    pytest = None

from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig
from backend.orchestrator.security.emergency_stop import EmergencyStopManager, emergency_stop_sandbox
from backend.orchestrator.security.approval_gate import ApprovalGate, SafetyLevel



def test_sandbox_config_defaults():
    """Verify SandboxConfig default values and Pydantic validation."""
    config = SandboxConfig(host_workspace_path=".")
    assert config.image_name == "ae01-sandbox:latest"
    assert config.cpu_count == 2.0
    assert config.memory_limit == "2g"
    assert config.network_mode == "none"


def test_sandbox_lifecycle_mock():
    """Verify DockerSandbox lifecycle in mock/dev mode."""
    config = SandboxConfig(host_workspace_path=".")
    sandbox = DockerSandbox(config)

    # Start container
    container_id = sandbox.start()
    assert container_id is not None
    assert sandbox.is_running() is True

    # Execute command
    res = sandbox.exec_command("echo 'Hello AE-01 Sandbox'")
    assert res.exit_code == 0
    assert "echo 'Hello AE-01 Sandbox'" in res.stdout

    # Stop container
    sandbox.stop()

    # Destroy container
    sandbox.destroy()
    assert sandbox.is_running() is False


def test_emergency_stop_manager():
    """Verify EmergencyStopManager registration and SIGKILL termination."""
    manager = EmergencyStopManager()
    manager.reset()

    config = SandboxConfig(host_workspace_path=".")
    sandbox = DockerSandbox(config)
    c_id = sandbox.start()

    manager.register_sandbox(c_id, sandbox)
    assert manager.is_stop_requested() is False

    # Trigger emergency stop
    stopped_count = manager.trigger_emergency_stop()
    assert stopped_count == 1
    assert manager.is_stop_requested() is True
    assert sandbox.is_running() is False


def test_approval_gate_policy():
    """Verify ApprovalGate auto-approval and dangerous command detection."""
    gate = ApprovalGate()

    # Safe command
    safe_res = gate.evaluate_command("pytest tests/")
    assert safe_res.safety_level == SafetyLevel.AUTO_APPROVED

    # Dangerous command
    danger_res = gate.evaluate_command("rm -rf /")
    assert danger_res.safety_level == SafetyLevel.REQUIRES_APPROVAL

    # Arbitrary command
    arb_res = gate.evaluate_command("which gcc")
    assert arb_res.safety_level == SafetyLevel.REQUIRES_APPROVAL
