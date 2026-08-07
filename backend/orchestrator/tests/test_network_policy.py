"""Unit tests for Network Policy Enforcer (NFR7, NFR8) (Member 4 Lead)."""

from backend.orchestrator.sandbox.network_policy import NetworkPolicyEnforcer, NetworkPolicyMode


def test_network_policy_default_deny_and_allowlist():
    """Verify default-deny enforcement and allowlist resolution."""
    # 1. DEFAULT_DENY Mode (network_mode="none")
    enforcer_deny = NetworkPolicyEnforcer(mode=NetworkPolicyMode.DEFAULT_DENY)
    assert enforcer_deny.get_docker_network_setting() == "none"
    assert enforcer_deny.is_host_allowed("pypi.org") is False
    assert enforcer_deny.is_host_allowed("google.com") is False

    # 2. ALLOWLIST_ONLY Mode (network_mode="bridge")
    enforcer_allow = NetworkPolicyEnforcer(mode=NetworkPolicyMode.ALLOWLIST_ONLY)
    assert enforcer_allow.get_docker_network_setting() == "bridge"

    # Default domains should be permitted
    assert enforcer_allow.is_host_allowed("pypi.org") is True
    assert enforcer_allow.is_host_allowed("registry.npmjs.org") is True

    # Arbitrary external domains blocked
    assert enforcer_allow.is_host_allowed("malicious-exfiltration-site.org") is False

    # Dynamic host addition
    enforcer_allow.add_allowed_host("api.github.com")
    assert enforcer_allow.is_host_allowed("api.github.com") is True
