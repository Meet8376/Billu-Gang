"""Sandbox Quick-Start Setup and Validation Script (Member 4 Lead).

Builds the base Docker sandbox image (ae01-sandbox:latest), validates Python dependencies,
and verifies Docker engine daemon connectivity.
"""

import os
import sys
import logging
from typing import Dict, Tuple

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

logger = logging.getLogger(__name__)


def check_python_environment() -> bool:
    """Validates Python version compatibility (Python 3.10+ required)."""
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 10:
        print(f"[OK] Python Environment OK: {sys.version.split()[0]}")
        return True
    else:
        print(f"[FAIL] Python 3.10+ required. Current version: {sys.version.split()[0]}")
        return False


def check_python_dependencies() -> Dict[str, bool]:
    """Validates presence of required Python packages from requirements.txt."""
    required_packages = ["docker", "pydantic", "langgraph", "typing_extensions"]
    results = {}

    for pkg in required_packages:
        try:
            __import__(pkg)
            results[pkg] = True
            print(f"[OK] Package '{pkg}' installed")
        except ImportError:
            results[pkg] = False
            print(f"[WARN] Package '{pkg}' missing (operating with fallback/mock layer)")

    return results


def check_docker_daemon() -> Tuple[bool, str]:
    """Checks if Docker daemon is running and reachable."""
    try:
        import docker
        client = docker.from_env()
        ping_ok = client.ping()
        print("[OK] Docker Daemon active and reachable")
        return True, "Docker daemon active"
    except Exception as e:
        msg = f"Docker daemon unavailable: {e}. Orchestrator operating in mock mode."
        print(f"[WARN] {msg}")
        return False, msg


def build_sandbox_docker_image() -> bool:
    """Builds the ae01-sandbox:latest Docker image from Dockerfile.sandbox."""
    dockerfile_path = os.path.join(os.path.dirname(__file__), "sandbox", "dockerfile", "Dockerfile.sandbox")
    if not os.path.exists(dockerfile_path):
        print(f"[FAIL] Dockerfile not found at: {dockerfile_path}")
        return False

    try:
        import docker
        client = docker.from_env()
        print(f"Building Docker image 'ae01-sandbox:latest' from {dockerfile_path}...")
        client.images.build(
            path=os.path.dirname(dockerfile_path),
            dockerfile="Dockerfile.sandbox",
            tag="ae01-sandbox:latest",
            rm=True
        )
        print("[OK] Docker sandbox image 'ae01-sandbox:latest' built successfully")
        return True
    except Exception as e:
        print(f"[WARN] Docker build skipped (daemon not connected): {e}")
        return False


def run_setup_validation() -> bool:
    """Runs complete quick-start setup validation suite."""
    print("=" * 60)
    print("      AE-01 Sandbox & Orchestrator Quick-Start Setup")
    print("=" * 60)

    py_ok = check_python_environment()
    deps_ok = check_python_dependencies()
    docker_ok, _ = check_docker_daemon()

    if docker_ok:
        build_sandbox_docker_image()

    print("=" * 60)
    print("Quick-Start Setup Validation Completed!")
    print("=" * 60)
    return py_ok


if __name__ == "__main__":
    run_setup_validation()
