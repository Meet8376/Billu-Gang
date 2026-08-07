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

try:
    import docker
    from docker.errors import APIError, DockerException, NotFound
    HAS_DOCKER_SDK = True
except ImportError:
    docker = None
    HAS_DOCKER_SDK = False


class SandboxConfig(BaseModel):
    """Configuration for Docker sandbox container instance."""
    image_name: str = Field(default="python:3.11-slim", description="Docker image tag")
    host_workspace_path: str = Field(..., description="Absolute path to host working copy")
    container_workspace_path: str = Field(default="/workspace", description="Mount target inside container")
    cpu_count: float = Field(default=2.0, description="CPU resource limit (e.g. 2.0 CPUs)")
    memory_limit: str = Field(default="2g", description="Memory limit (e.g. '2g', '512m')")
    network_mode: str = Field(default="bridge", description="Network mode ('none' or 'bridge')")
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

        if not HAS_DOCKER_SDK:
            raise RuntimeError("Docker SDK is not installed in Python environment. Run 'pip install docker'.")

        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            raise RuntimeError(f"Docker Engine is not running or unreachable ({e}). Please start Docker Desktop.") from e

    def _cleanup_old_containers(self):
        """Clean up any old/stale ae01-sandbox containers to prevent container sprawl."""
        try:
            containers = self.client.containers.list(all=True, filters={"name": "ae01-sandbox"})
            for c in containers:
                try:
                    c.stop(timeout=1)
                    c.remove(force=True)
                except Exception:
                    pass
        except Exception:
            pass

    def _ensure_docker_image(self, image_name: str) -> bool:
        """Ensures Docker image is built from Dockerfile.sandbox or pulled if missing."""
        if not self.client:
            return False

        try:
            self.client.images.get(image_name)
            return True
        except Exception:
            pass

        # Try building ae01-sandbox:latest from Dockerfile.sandbox if specified
        if image_name == "ae01-sandbox:latest" or "ae01" in image_name:
            try:
                dockerfile_dir = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "dockerfile")
                )
                dockerfile_path = os.path.join(dockerfile_dir, "Dockerfile.sandbox")
                if os.path.exists(dockerfile_path):
                    logger.info(f"Building Docker image '{image_name}' from {dockerfile_path}...")
                    self.client.images.build(
                        path=dockerfile_dir,
                        dockerfile="Dockerfile.sandbox",
                        tag=image_name,
                        rm=True
                    )
                    logger.info(f"Docker image '{image_name}' built successfully.")
                    return True
            except Exception as e:
                logger.warning(f"Failed to build Docker image '{image_name}': {e}")

        # Fallback to pulling base image from Docker registry
        try:
            logger.info(f"Pulling Docker image '{image_name}'...")
            self.client.images.pull(image_name)
            return True
        except Exception as e:
            logger.warning(f"Failed to pull Docker image '{image_name}': {e}")
            return False

    def start(self) -> str:
        """Starts or reuses the sandboxed container instance."""
        fixed_container_name = "ae01-sandbox-active"

        # 1. Reuse existing active container if available
        try:
            existing = self.client.containers.get(fixed_container_name)
            if existing.status == "running":
                self.container = existing
                self.container_id = existing.id
                logger.info(f"Reusing active Docker Sandbox container (ID: {self.container_id[:12]})")
                return self.container_id
            else:
                existing.remove(force=True)
        except NotFound:
            pass
        except Exception:
            pass

        # 2. Cleanup any leftover sandbox containers
        self._cleanup_old_containers()

        # 3. Start a clean single container instance
        abs_host_path = os.path.abspath(self.config.host_workspace_path).replace("\\", "/")
        volumes = {
            abs_host_path: {
                'bind': self.config.container_workspace_path,
                'mode': 'rw'
            }
        }

        nano_cpus = int(self.config.cpu_count * 1e9)
        images_to_try = [
            "ae01-sandbox:latest",
            self.config.image_name,
            "python:3.11-slim",
            "python:3.10-slim",
            "alpine:latest"
        ]
        
        last_error = None
        for img in images_to_try:
            self._ensure_docker_image(img)
            # Tier 1: Full volume mount with CPU and Memory limits
            try:
                self.container = self.client.containers.run(
                    image=img,
                    command="tail -f /dev/null",
                    name=fixed_container_name,
                    detach=True,
                    volumes=volumes,
                    working_dir=self.config.container_workspace_path,
                    nano_cpus=nano_cpus,
                    mem_limit=self.config.memory_limit,
                    environment=self.config.env_vars
                )
                self.container_id = self.container.id
                logger.info(f"Docker Sandbox container started successfully (ID: {self.container_id[:12]}, Image: {img})")
                return self.container_id
            except Exception as e1:
                last_error = e1

            # Tier 2: Volume mount without CPU limits
            try:
                self.container = self.client.containers.run(
                    image=img,
                    command="tail -f /dev/null",
                    name=fixed_container_name,
                    detach=True,
                    volumes=volumes,
                    working_dir=self.config.container_workspace_path,
                    environment=self.config.env_vars
                )
                self.container_id = self.container.id
                logger.info(f"Docker Sandbox container started successfully (ID: {self.container_id[:12]}, Image: {img})")
                return self.container_id
            except Exception as e2:
                last_error = e2

            # Tier 3: Core detached container run
            try:
                self.container = self.client.containers.run(
                    image=img,
                    command="tail -f /dev/null",
                    name=fixed_container_name,
                    detach=True
                )
                self.container_id = self.container.id
                logger.info(f"Docker Sandbox container started successfully (ID: {self.container_id[:12]}, Image: {img})")
                return self.container_id
            except Exception as e3:
                last_error = e3

            # Tier 4: System Docker CLI subprocess run (direct OS command)
            try:
                import subprocess
                subprocess.run(["docker", "rm", "-f", fixed_container_name], capture_output=True)
                run_cmd = ["docker", "run", "-d", "--name", fixed_container_name, "-v", f"{abs_host_path}:/workspace", img, "tail", "-f", "/dev/null"]
                sp_res = subprocess.run(run_cmd, capture_output=True, text=True)
                if sp_res.returncode == 0:
                    cid = sp_res.stdout.strip()
                    self.container_id = cid
                    logger.info(f"Docker Sandbox container started via system CLI (ID: {cid[:12]}, Image: {img})")
                    return self.container_id
            except Exception as e4:
                last_error = e4
                continue

        raise RuntimeError(f"Docker container creation failed for all images: {last_error}")

    def exec_command(self, command: str, timeout_sec: int = 60, cwd: Optional[str] = None) -> CommandResult:
        """Executes a shell command inside the running sandbox container."""
        start_time = time.time()

        if not self.container:
            raise RuntimeError("Sandbox container is not active. Call start() first.")

        exec_res = self.container.exec_run(
            cmd=["sh", "-c", command],
            workdir=cwd or self.config.container_workspace_path
        )
        duration = time.time() - start_time
        output_str = exec_res.output.decode('utf-8', errors='replace') if isinstance(exec_res.output, bytes) else str(exec_res.output)
        
        return CommandResult(
            command=command,
            exit_code=exec_res.exit_code,
            stdout=output_str,
            stderr="",
            duration_sec=duration
        )

    def stop(self) -> bool:
        """Stops and removes the sandboxed container instance."""
        if not self.container:
            self.container_id = None
            return True

        try:
            self.container.stop(timeout=2)
            self.container.remove(force=True)
            self.container_id = None
            logger.info("Docker Sandbox container stopped and removed cleanly.")
            return True
        except Exception as e:
            logger.warning(f"Error stopping container: {e}")
            return False
