"""Emergency Stop Handler for Docker Sandbox Execution (Member 4 Lead).

Instantly halts container executions and sends SIGKILL to sandbox processes
when a user triggers Ctrl+C, /pause, or an emergency abort request.
"""

import logging
import threading
from typing import Dict, List, Optional, Tuple
from backend.orchestrator.sandbox.docker_manager import DockerSandbox

logger = logging.getLogger(__name__)


class EmergencyStopManager:
    """Registry and manager for emergency termination of sandboxed containers."""

    _instance: Optional['EmergencyStopManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'EmergencyStopManager':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._sandboxes: Dict[str, DockerSandbox] = {}
                cls._instance._stop_requested = False
                cls._instance._paused = False
            return cls._instance

    def register_sandbox(self, sandbox_id: str, sandbox: DockerSandbox) -> None:
        """Registers an active sandbox container for emergency tracking."""
        with self._lock:
            self._sandboxes[sandbox_id] = sandbox
            logger.debug(f"Registered sandbox {sandbox_id[:12]} in EmergencyStopManager")

    def unregister_sandbox(self, sandbox_id: str) -> None:
        """Unregisters a sandbox container after normal completion."""
        with self._lock:
            self._sandboxes.pop(sandbox_id, None)
            logger.debug(f"Unregistered sandbox {sandbox_id[:12]} from EmergencyStopManager")

    def is_stop_requested(self) -> bool:
        """Checks if an emergency stop signal has been issued."""
        return self._stop_requested

    def is_paused(self) -> bool:
        """Checks if execution is currently paused by /pause command."""
        return self._paused

    def pause_execution(self) -> None:
        """Pauses active task orchestrator execution graph (/pause route)."""
        with self._lock:
            self._paused = True
            logger.info("Task orchestrator execution PAUSED by user request")

    def resume_execution(self) -> None:
        """Resumes active task orchestrator execution graph."""
        with self._lock:
            self._paused = False
            logger.info("Task orchestrator execution RESUMED")

    def trigger_emergency_stop(self, sandbox_id: Optional[str] = None) -> int:
        """Instantly terminates specified sandbox or all active sandboxes (SIGKILL)."""
        stopped_count = 0
        with self._lock:
            self._stop_requested = True
            self._paused = False
            targets: List[Tuple[str, DockerSandbox]] = []

            if sandbox_id:
                if sandbox_id in self._sandboxes:
                    targets.append((sandbox_id, self._sandboxes[sandbox_id]))
            else:
                targets = list(self._sandboxes.items())

            for s_id, sandbox in targets:
                try:
                    logger.warning(f"EMERGENCY STOP: Killing sandbox container {s_id[:12]}")
                    sandbox.destroy()
                    stopped_count += 1
                except Exception as e:
                    logger.error(f"Error during emergency stop of sandbox {s_id[:12]}: {e}")

            if sandbox_id:
                self._sandboxes.pop(sandbox_id, None)
            else:
                self._sandboxes.clear()

        return stopped_count

    def reset(self) -> None:
        """Resets emergency stop status flags."""
        with self._lock:
            self._stop_requested = False
            self._paused = False
            self._sandboxes.clear()


# Global helper function for convenience
def emergency_stop_sandbox(sandbox_id: Optional[str] = None) -> int:
    """Helper function to trigger emergency stop globally."""
    manager = EmergencyStopManager()
    return manager.trigger_emergency_stop(sandbox_id)
