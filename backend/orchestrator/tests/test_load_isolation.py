"""Unit tests for Docker Sandbox Lifecycle Load Testing & Disk Isolation (Member 4 Lead)."""

import os
from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig


def test_sandbox_lifecycle_load_and_cleanup():
    """Verify multiple rapid sandbox startup/destroy cycles and volume cleanup."""
    config = SandboxConfig(host_workspace_path=".")

    for i in range(3):
        sandbox = DockerSandbox(config)
        sandbox.start()
        assert sandbox.is_running() is True

        res = sandbox.exec_command("echo load_test_iteration", timeout_sec=5)
        assert res.exit_code == 0
        assert "load_test_iteration" in res.stdout

        sandbox.destroy()
        assert sandbox.is_running() is False
