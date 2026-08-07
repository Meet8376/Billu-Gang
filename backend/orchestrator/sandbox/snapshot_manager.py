"""Filesystem Snapshot and Git Checkpoint Manager (Member 4 Lead).

Provides git commit / patch snapshotting inside the sandbox workspace
to enable instant rollback (/rollback) and patch generation.
"""

import logging
import os
import time
import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.orchestrator.sandbox.docker_manager import DockerSandbox

logger = logging.getLogger(__name__)


class SnapshotMetadata(BaseModel):
    """Metadata for a filesystem snapshot checkpoint."""
    snapshot_id: str = Field(default_factory=lambda: f"snap-{uuid.uuid4().hex[:8]}")
    step_name: str
    timestamp: float = Field(default_factory=time.time)
    commit_hash: Optional[str] = None
    description: str


class SnapshotManager:
    """Manages git-based workspace checkpoints, rollbacks, and patch exports."""

    def __init__(self, sandbox: DockerSandbox):
        self.sandbox = sandbox
        self.snapshots: List[SnapshotMetadata] = []
        self._initial_commit: Optional[str] = None

    def initialize_workspace_git(self) -> None:
        """Ensures workspace is a valid git repository and records baseline commit."""
        res = self.sandbox.exec_command("git rev-parse --is-inside-work-tree")
        if res.exit_code != 0:
            # Initialize git repo in workspace if not already present
            self.sandbox.exec_command("git init")
            self.sandbox.exec_command("git config user.name 'AE01-Sandbox'")
            self.sandbox.exec_command("git config user.email 'sandbox@ae01.local'")
            self.sandbox.exec_command("git add .")
            self.sandbox.exec_command("git commit -m 'AE-01 Baseline Initial Commit'")

        res_head = self.sandbox.exec_command("git rev-parse HEAD")
        if res_head.exit_code == 0:
            self._initial_commit = res_head.stdout.strip()
            logger.info(f"Workspace Git baseline initialized at commit {self._initial_commit[:8]}")

    def create_checkpoint(self, step_name: str, description: str = "") -> SnapshotMetadata:
        """Creates a snapshot commit checkpoint before or after code edits."""
        if not self._initial_commit:
            self.initialize_workspace_git()

        snap = SnapshotMetadata(
            step_name=step_name,
            description=description or f"Snapshot checkpoint for step: {step_name}"
        )

        # Stage and commit current working tree state
        self.sandbox.exec_command("git add -A")
        commit_msg = f"AE-01 Checkpoint [{snap.snapshot_id}]: {step_name}"
        res_commit = self.sandbox.exec_command(f"git commit --allow-empty -m '{commit_msg}'")

        res_hash = self.sandbox.exec_command("git rev-parse HEAD")
        if res_hash.exit_code == 0:
            snap.commit_hash = res_hash.stdout.strip()

        self.snapshots.append(snap)
        logger.info(f"Created snapshot checkpoint '{snap.snapshot_id}' at commit {snap.commit_hash[:8] if snap.commit_hash else 'N/A'}")
        return snap

    def rollback_to_snapshot(self, snapshot_id: str) -> bool:
        """Reverts the workspace cleanly to a specific snapshot checkpoint."""
        target_snap = next((s for s in self.snapshots if s.snapshot_id == snapshot_id), None)
        target_hash = target_snap.commit_hash if target_snap else self._initial_commit

        if not target_hash:
            logger.error(f"Cannot rollback: Target commit hash for snapshot {snapshot_id} not found.")
            return False

        # Reset working tree hard to target commit hash
        res = self.sandbox.exec_command(f"git reset --hard {target_hash}")
        res_clean = self.sandbox.exec_command("git clean -fd")

        if res.exit_code == 0:
            logger.info(f"Successfully rolled back workspace to snapshot {snapshot_id} (commit {target_hash[:8]})")
            return True
        else:
            logger.error(f"Rollback failed: {res.stderr}")
            return False

    def rollback_to_baseline(self) -> bool:
        """Reverts workspace completely to initial clean baseline state."""
        if not self._initial_commit:
            logger.warning("No baseline commit recorded. Skipping rollback.")
            return False

        res = self.sandbox.exec_command(f"git reset --hard {self._initial_commit}")
        self.sandbox.exec_command("git clean -fd")
        return res.exit_code == 0

    def generate_patch(self) -> str:
        """Generates unified git diff patch representing changes from baseline."""
        if not self._initial_commit:
            return ""

        res = self.sandbox.exec_command(f"git diff {self._initial_commit} HEAD")
        return res.stdout if res.exit_code == 0 else ""

    def list_snapshots(self) -> List[SnapshotMetadata]:
        """Returns list of recorded snapshot checkpoints."""
        return self.snapshots
