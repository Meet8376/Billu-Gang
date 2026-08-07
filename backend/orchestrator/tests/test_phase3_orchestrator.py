"""Unit tests for Member 4 Phase 3 Sandbox Isolation, Security & Agent Nodes."""

import asyncio
from backend.orchestrator.graph.agent_nodes import coder_node, planner_node, reproduce_node, reviewer_node, verifier_node
from backend.orchestrator.graph.task_planner import TaskNode, TaskType
from backend.orchestrator.sandbox.container_exec import ContainerExecService
from backend.orchestrator.sandbox.docker_manager import DockerSandbox, SandboxConfig
from backend.orchestrator.sandbox.network_policy import NetworkPolicyEnforcer, NetworkPolicyMode
from backend.orchestrator.sandbox.snapshot_manager import SnapshotManager
from backend.orchestrator.security.secret_redactor import SecretRedactor, redact_secrets


def test_secret_redactor():
    """Verify secret redactor scrubs API keys and registered tokens."""
    redactor = SecretRedactor()

    # Test OpenAI API key scrubbing
    raw_key_text = "Connecting with API key sk-proj-1234567890abcdef1234567890abcdef"
    clean_text = redactor.redact(raw_key_text)
    assert "sk-proj-" not in clean_text
    assert "[REDACTED_SECRET]" in clean_text

    # Test registered custom token scrubbing
    redactor.register_secret("my_super_secret_password_123")
    clean_custom = redactor.redact("Login attempt with password my_super_secret_password_123")
    assert "my_super_secret_password_123" not in clean_custom
    assert "[REDACTED_SECRET]" in clean_custom


def test_network_policy_enforcer():
    """Verify default-deny network policy enforcement."""
    # Default Deny Mode
    policy_deny = NetworkPolicyEnforcer(mode=NetworkPolicyMode.DEFAULT_DENY)
    assert policy_deny.get_docker_network_setting() == "none"
    assert policy_deny.is_host_allowed("pypi.org") is False

    # Allowlist Mode
    policy_allow = NetworkPolicyEnforcer(mode=NetworkPolicyMode.ALLOWLIST_ONLY)
    assert policy_allow.get_docker_network_setting() == "bridge"
    assert policy_allow.is_host_allowed("pypi.org") is True
    assert policy_allow.is_host_allowed("unauthorized-malicious-site.com") is False


def test_agent_nodes_execution():
    """Verify agent nodes execution (planner, reproduce, coder, verifier, reviewer)."""
    # 1. Planner Node
    state = asyncio.run(planner_node("sess-p3", "Fix pagination bug"))
    assert len(state.nodes) == 5

    # Setup Sandbox & Services
    config = SandboxConfig(host_workspace_path=".")
    sandbox = DockerSandbox(config)
    sandbox.start()

    exec_service = ContainerExecService(sandbox)
    snapshot_mgr = SnapshotManager(sandbox)

    # 2. Reproduce Node
    repro_node = TaskNode(title="Repro", description="Repro", task_type=TaskType.REPRODUCE)
    repro_res = asyncio.run(reproduce_node(repro_node, exec_service))
    assert repro_res["node_id"] == repro_node.id

    # 3. Coder Node
    code_node = TaskNode(title="Coder", description="Coder", task_type=TaskType.EDIT)
    coder_res = asyncio.run(coder_node(code_node, exec_service, snapshot_mgr))
    assert coder_res["snapshot_id"].startswith("snap-")

    # 4. Reviewer Node
    rev_node = TaskNode(title="Reviewer", description="Reviewer", task_type=TaskType.REVIEW)
    rev_res = asyncio.run(reviewer_node(rev_node, snapshot_mgr))
    assert rev_res["verified_complete"] is True

    sandbox.destroy()
