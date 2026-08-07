"""Docker Sandbox Execution Manager (Member 4 Lead).

Manages Docker container lifecycles, volume mounts, resource caps (CPU/Memory),
and safe command execution inside isolated sandbox environments.
"""

import logging
import os
import time
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try importing docker SDK; fall back gracefully if missing or daemon unavailable
try:
    import docker
    from docker.errors import APIError, DockerException, NotFound
    HAS_DOCKER_SDK = True
except ImportError:
    docker = None
    HAS_DOCKER_SDK = False


class SandboxConfig(BaseModel):
    """Configuration for Docker sandbox container instance."""
    image_name: str = Field(default="ae01-sandbox:latest", description="Docker image tag")
    host_workspace_path: str = Field(..., description="Absolute path to host working copy")
    container_workspace_path: str = Field(default="/workspace", description="Mount target inside container")
    cpu_count: float = Field(default=2.0, description="CPU resource limit (e.g. 2.0 CPUs)")
    memory_limit: str = Field(default="2g", description="Memory limit (e.g. '2g', '512m')")
    network_mode: str = Field(default="none", description="Network mode ('none' for default-deny, 'bridge' for allowed)")
    read_only_rootfs: bool = Field(default=False, description="Whether root filesystem is read-only")
    env_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables passed into sandbox")


class CommandResult(BaseModel):
    """Result of command executed inside sandbox container."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_sec: float
    timed_out: bool = False


class DockerSandbox:
    """Manages an isolated Docker container instance for sandboxed tool execution."""

    def __init__(self, config: SandboxConfig):
        self.config = config
        self.client: Optional[docker.DockerClient] = None
        self.container = None
        self.container_id: Optional[str] = None
        self._is_mock: bool = False

        if HAS_DOCKER_SDK:
            try:
                self.client = docker.from_env()
            except Exception as e:
                logger.warning(f"Docker daemon connection failed ({e}). Operating in mock mode.")
                self._is_mock = True
        else:
            logger.warning("docker SDK not installed. Operating in mock mode.")
            self._is_mock = True

    def start(self) -> str:
        """Starts the sandboxed container with volume mounts and resource caps."""
        if self._is_mock:
            self.container_id = "mock-sandbox-container-id"
            logger.info(f"Mock Docker Sandbox initialized for path {self.config.host_workspace_path}")
            return self.container_id

        abs_host_path = os.path.abspath(self.config.host_workspace_path)
        volumes = {
            abs_host_path: {
                'bind': self.config.container_workspace_path,
                'mode': 'rw'
            }
        }

        # Convert CPU limit to nanoCPUs for Docker SDK
        nano_cpus = int(self.config.cpu_count * 1e9)

        try:
            self.container = self.client.containers.run(
                image=self.config.image_name,
                command="tail -f /dev/null",  # Keep container running for exec calls
                detach=True,
                volumes=volumes,
                working_dir=self.config.container_workspace_path,
                nano_cpus=nano_cpus,
                mem_limit=self.config.memory_limit,
                network_mode=self.config.network_mode,
                read_only=self.config.read_only_rootfs,
                environment=self.config.env_vars,
                user="sandboxuser",
                security_opt=["no-new-privileges:true"]
            )
            self.container_id = self.container.id
            logger.info(f"Docker Sandbox container started successfully (ID: {self.container_id[:12]})")
            return self.container_id
        except Exception as e:
            logger.error(f"Failed to start Docker container: {e}")
            raise RuntimeError(f"Sandbox container creation failed: {e}") from e

    def exec_command(self, command: str, timeout_sec: int = 60, cwd: Optional[str] = None) -> CommandResult:
        """Executes a shell command inside the running sandbox container."""
        start_time = time.time()
        work_dir = cwd or self.config.container_workspace_path

        if self._is_mock:
            duration = time.time() - start_time
            logger.info(f"[Mock Exec] {command}")
            return CommandResult(
                command=command,
                exit_code=0,
                stdout=f"[Mock Sandbox Stdout] Ran command: {command}",
                stderr="",
                duration_sec=duration,
                timed_out=False
            )

        if not self.container or not self.is_running():
            raise RuntimeError("Sandbox container is not currently running.")

        try:
            # Wrap command in bash shell call
            full_cmd = ["/bin/bash", "-c", command]
            exec_res = self.container.exec_run(
                cmd=full_cmd,
                workdir=work_dir,
                demux=True  # Separate stdout and stderr
            )

            duration = time.time() - start_time
            stdout_bytes, stderr_bytes = exec_res.output

            stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
            stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""

            return CommandResult(
                command=command,
                exit_code=exec_res.exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_sec=duration,
                timed_out=False
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error executing command inside container: {e}")
            return CommandResult(
                command=command,
                exit_code=137,
                stdout="",
                stderr=str(e),
                duration_sec=duration,
                timed_out=False
            )

    def is_running(self) -> bool:
        """Returns True if the sandbox container is currently active."""
        if self._is_mock:
            return self.container_id is not None

        if not self.container:
            return False

        try:
            self.container.reload()
            return self.container.status == 'running'
        except Exception:
            return False

    def stop(self, timeout_sec: int = 5) -> None:
        """Stops the container gracefully."""
        if self._is_mock:
            logger.info("Mock Docker Sandbox stopped.")
            return

        if self.container:
            try:
                self.container.stop(timeout=timeout_sec)
                logger.info(f"Docker Sandbox container stopped (ID: {self.container_id[:12]})")
            except Exception as e:
                logger.warning(f"Error stopping sandbox container: {e}")

    def destroy(self) -> None:
        """Forcefully kills and removes the container."""
        if self._is_mock:
            self.container_id = None
            logger.info("Mock Docker Sandbox destroyed.")
            return

        if self.container:
            try:
                self.container.remove(force=True)
                logger.info(f"Docker Sandbox container force-removed (ID: {self.container_id[:12]})")
            except Exception as e:
                logger.warning(f"Error removing sandbox container: {e}")
            finally:
                self.container = None
                self.container_id = None
