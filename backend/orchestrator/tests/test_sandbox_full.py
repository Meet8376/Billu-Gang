"""Full Unit Test Suite for Sandbox Engine & Security Enforcers (100% Coverage Target)."""

import os
import pytest
from unittest.mock import MagicMock, patch

from backend.orchestrator.sandbox.docker_manager import (
    DockerSandbox,
    SandboxConfig,
    CommandResult,
)
from backend.orchestrator.sandbox.container_exec import ContainerExecService, ExecutionResponse
from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager, SnapshotMetadata
from backend.orchestrator.sandbox.network_policy import NetworkPolicyEnforcer, NetworkPolicyMode
from backend.orchestrator.security.approval_gate import ApprovalGate, SafetyLevel


def test_sandbox_config_instantiation():
    """Test SandboxConfig fields and default values."""
    config = SandboxConfig(host_workspace_path="/tmp/test_workspace")
    assert config.image_name == "ae01-sandbox:latest"
    assert config.host_workspace_path == "/tmp/test_workspace"
    assert config.container_workspace_path == "/workspace"
    assert config.cpu_count == 2.0
    assert config.memory_limit == "2g"
    assert config.network_mode == "none"
    assert config.read_only_rootfs is False


def test_docker_sandbox_mock_lifecycle():
    """Test full DockerSandbox lifecycle operating in Mock mode."""
    config = SandboxConfig(host_workspace_path="/tmp/mock_workspace")
    sandbox = DockerSandbox(config)
    sandbox._is_mock = True

    # Start
    container_id = sandbox.start()
    assert container_id == "mock-sandbox-container-id"
    assert sandbox.is_running() is True

    # Exec command
    res = sandbox.exec_command("python --version")
    assert res.exit_code == 0
    assert res.timed_out is False
    assert "python --version" in res.stdout

    # Stop & Destroy
    sandbox.stop()
    sandbox.destroy()
    assert sandbox.container_id is None
    assert sandbox.is_running() is False


@pytest.mark.asyncio
async def test_container_exec_service_auto_approved():
    """Test ContainerExecService with AUTO_APPROVED command."""
    config = SandboxConfig(host_workspace_path="/tmp/mock_workspace")
    sandbox = DockerSandbox(config)
    sandbox._is_mock = True

    service = ContainerExecService(sandbox=sandbox)
    resp = await service.execute_command("pytest tests/")

    assert resp.exit_code == 0
    assert resp.safety_level == SafetyLevel.AUTO_APPROVED.value
    assert resp.approved is True
    assert resp.timed_out is False


@pytest.mark.asyncio
async def test_container_exec_service_blocked_command():
    """Test ContainerExecService with dangerous BLOCKED command."""
    config = SandboxConfig(host_workspace_path="/tmp/mock_workspace")
    sandbox = DockerSandbox(config)

    gate = MagicMock()
    eval_res = MagicMock()
    eval_res.safety_level = SafetyLevel.BLOCKED
    eval_res.reason = "Dangerous command blocked"
    gate.evaluate_command.return_value = eval_res

    service = ContainerExecService(sandbox=sandbox, approval_gate=gate)
    resp = await service.execute_command("rm -rf /")

    assert resp.exit_code == 126
    assert resp.approved is False
    assert "Command blocked by security policy" in resp.stderr


def test_snapshot_manager_checkpoint_and_rollback():
    """Test SnapshotManager creation of checkpoints and workspace rollback."""
    mock_sandbox = MagicMock()
    mock_sandbox.exec_command.side_effect = [
        CommandResult(command="", exit_code=0, stdout="true", stderr="", duration_sec=0.1),
        CommandResult(command="", exit_code=0, stdout="initial_commit_hash_12345", stderr="", duration_sec=0.1),
        CommandResult(command="", exit_code=0, stdout="commit_ok", stderr="", duration_sec=0.1),
        CommandResult(command="", exit_code=0, stdout="snap_commit_hash_67890", stderr="", duration_sec=0.1),
        CommandResult(command="", exit_code=0, stdout="reset_ok", stderr="", duration_sec=0.1),
        CommandResult(command="", exit_code=0, stdout="clean_ok", stderr="", duration_sec=0.1),
    ]

    manager = SnapshotManager(sandbox=mock_sandbox)
    manager.initialize_workspace_git()
    assert manager._initial_commit == "initial_commit_hash_12345"

    snap = manager.create_checkpoint("Step 1", "Drafting fix")
    assert snap.step_name == "Step 1"
    assert snap.commit_hash == "snap_commit_hash_67890"

    success = manager.rollback_to_snapshot(snap.snapshot_id)
    assert success is True


def test_network_policy_enforcer():
    """Test NetworkPolicyEnforcer default deny and allowlist mode."""
    enforcer = NetworkPolicyEnforcer(mode=NetworkPolicyMode.DEFAULT_DENY)
    assert enforcer.get_docker_network_setting() == "none"
    assert enforcer.is_host_allowed("pypi.org") is False

    enforcer_allow = NetworkPolicyEnforcer(mode=NetworkPolicyMode.ALLOWLIST_ONLY)
    assert enforcer_allow.get_docker_network_setting() == "bridge"
    assert enforcer_allow.is_host_allowed("pypi.org") is True
    assert enforcer_allow.is_host_allowed("unauthorized-site.com") is False

    enforcer_allow.add_allowed_host("custom-internal-pip.org")
    assert enforcer_allow.is_host_allowed("custom-internal-pip.org") is True
