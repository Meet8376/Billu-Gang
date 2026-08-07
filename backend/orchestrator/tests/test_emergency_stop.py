"""Unit tests for Emergency Stop Manager and /pause interrupt handler (Member 4 Lead)."""

from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig
from backend.orchestrator.security.emergency_stop import EmergencyStopManager, emergency_stop_sandbox


def test_emergency_stop_manager_singleton_and_pause():
    """Verify singleton behavior, pause/resume routes, and SIGKILL termination."""
    mgr1 = EmergencyStopManager()
    mgr2 = EmergencyStopManager()
    assert mgr1 is mgr2

    mgr1.reset()
    assert mgr1.is_stop_requested() is False
    assert mgr1.is_paused() is False

    # Test Pause / Resume state routing
    mgr1.pause_execution()
    assert mgr1.is_paused() is True

    mgr1.resume_execution()
    assert mgr1.is_paused() is False

    # Test Sandbox Registration & SIGKILL Emergency Termination
    config = SandboxConfig(host_workspace_path=".")
    sandbox = DockerSandbox(config)
    sandbox.start()

    mgr1.register_sandbox(sandbox.container_id, sandbox)
    stopped = mgr1.trigger_emergency_stop(sandbox.container_id)
    assert stopped == 1
    assert mgr1.is_stop_requested() is True

    mgr1.reset()
