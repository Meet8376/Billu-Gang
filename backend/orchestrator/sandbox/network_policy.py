"""Sandbox Network Policy and Isolation Enforcer (Member 4 Lead).

Enforces default-deny network rules (NFR7, NFR8) preventing unauthorized host,
local intranet, or external internet access from inside the Docker sandbox container.
"""

import logging
from enum import Enum
from typing import List, Set

logger = logging.getLogger(__name__)


class NetworkPolicyMode(str, Enum):
    DEFAULT_DENY = "DEFAULT_DENY"      # network_mode = "none" (completely isolated)
    ALLOWLIST_ONLY = "ALLOWLIST_ONLY"  # network_mode = "bridge" with iptables/host filters
    UNRESTRICTED = "UNRESTRICTED"      # Disabled (not permitted for security compliance)


class NetworkPolicyEnforcer:
    """Configures and enforces sandbox container network security policies."""

    # Default allowed host domains when explicit allowlist is active (e.g. package mirrors)
    DEFAULT_ALLOWLIST: Set[str] = {
        "pypi.org",
        "files.pythonhosted.org",
        "registry.npmjs.org",
        "deb.debian.org",
        "nodesource.com"
    }

    def __init__(self, mode: NetworkPolicyMode = NetworkPolicyMode.DEFAULT_DENY):
        self.mode = mode
        self.allowlist: Set[str] = set(self.DEFAULT_ALLOWLIST)

    def add_allowed_host(self, host: str) -> None:
        """Adds a host domain to the active allowlist."""
        self.allowlist.add(host.lower().strip())
        logger.info(f"Added host '{host}' to sandbox network allowlist")

    def is_host_allowed(self, host: str) -> bool:
        """Checks whether outbound connection to a target host is permitted."""
        if self.mode == NetworkPolicyMode.DEFAULT_DENY:
            logger.warning(f"Network access DENIED (DEFAULT_DENY mode active): target '{host}'")
            return False

        if self.mode == NetworkPolicyMode.ALLOWLIST_ONLY:
            host_clean = host.lower().strip()
            is_allowed = any(host_clean.endswith(domain) for domain in self.allowlist)
            if not is_allowed:
                logger.warning(f"Network access DENIED (Host '{host}' not in allowlist)")
            return is_allowed

        return False  # UNRESTRICTED is blocked by safety compliance

    def get_docker_network_setting(self) -> str:
        """Returns Docker network mode parameter for container configuration."""
        if self.mode == NetworkPolicyMode.DEFAULT_DENY:
            return "none"
        else:
            return "bridge"
