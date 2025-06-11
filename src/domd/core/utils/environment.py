"""
Environment detection and Docker execution utilities for command execution.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union

import docker
from docker.models.containers import Container


class EnvironmentDetector:
    """Detects the execution environment and manages Docker operations."""

    def __init__(self, project_root: Union[str, Path] = "."):
        """Initialize the environment detector.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.docker_client = None
        self._dodocker_config = {}
        self._init_docker_client()
        self._dodocker_path = self.project_root / ".dodocker"
        self._dodocker_config = self._load_dodocker_config()

    def _init_docker_client(self):
        """Initialize Docker client if Docker is available."""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()  # Verify connection
        except Exception:
            self.docker_client = None

    def _load_dodocker_config(self) -> Dict[str, dict]:
        """Load commands that should run in Docker from .dodocker file.

        Returns:
            Dictionary mapping command patterns to their Docker configurations
        """
        if not self._dodocker_path.exists():
            return {}

        import yaml

        try:
            with open(self._dodocker_path, "r") as f:
                config = yaml.safe_load(f) or {}
                # Convert to a dictionary with string keys
                return {str(k): v for k, v in config.items()}
        except (yaml.YAMLError, IOError):
            return {}

    def get_docker_config(self, command: str) -> Optional[Dict]:
        """Get Docker configuration for a command.

        Args:
            command: The command to get Docker config for

        Returns:
            Optional[Dict]: Docker configuration if command should run in Docker, None otherwise
        """
        if not self.docker_client:
            return None

        # Check if command matches any pattern in .dodocker
        for pattern, config in self._dodocker_config.items():
            if pattern in command:
                return config

        return None

    def should_use_docker(self, command: str) -> bool:
        """Determine if a command should run in Docker.

        Args:
            command: The command string to check

        Returns:
            bool: True if the command should run in Docker
        """
        return self.get_docker_config(command) is not None

    def _expand_paths(self, config: Dict) -> Dict:
        """Expand paths in Docker configuration.

        Args:
            config: Docker configuration dictionary

        Returns:
            Dict: Configuration with expanded paths
        """
        if not config:
            return config

        expanded = config.copy()

        # Handle volumes
        if "volumes" in expanded and isinstance(expanded["volumes"], dict):
            expanded_volumes = {}
            for host_path, container_path in expanded["volumes"].items():
                # Handle both string and dict formats
                expanded_volumes[os.path.expanduser(host_path)] = container_path
            expanded["volumes"] = expanded_volumes

        return expanded

    def execute_in_docker(
        self,
        command: str,
        image: str = "python:3.9-slim",
        volumes: Optional[Dict[str, dict]] = None,
        environment: Optional[Dict[str, str]] = None,
        workdir: Optional[str] = None,
        privileged: bool = False,
        ports: Optional[Dict[str, str]] = None,
    ) -> int:
        """Execute a command in a Docker container.

        Args:
            command: Command to execute
            image: Docker image to use
            volumes: Volume mappings
            environment: Environment variables
            workdir: Working directory in container

        Returns:
            int: Exit code of the command
        """
        if not self.docker_client:
            raise RuntimeError("Docker is not available")

        # Default volumes: mount project directory
        volumes = volumes or {str(self.project_root): {"bind": "/app", "mode": "rw"}}

        # Default working directory
        workdir = workdir or "/app"

        # Initialize ports if not provided
        ports = ports or {}

        container_kwargs = {
            "image": image,
            "command": ["/bin/sh", "-c", command],
            "volumes": volumes or {},
            "environment": environment or {},
            "working_dir": workdir or "/app",
            "detach": True,
            "tty": True,
            "remove": True,
            "stdout": True,
            "stderr": True,
            "privileged": privileged,
        }

        # Add port mappings if specified
        if ports:
            container_kwargs["ports"] = ports

        try:
            container: Container = self.docker_client.containers.run(**container_kwargs)

            # Stream logs
            for line in container.logs(stream=True, follow=True):
                print(line.decode().strip())

            # Wait for container to finish and get exit code
            result = container.wait()
            return result.get("StatusCode", 1)

        except docker.errors.ContainerError as e:
            print(f"Docker container failed: {e}")
            return e.exit_status
        except docker.errors.ImageNotFound:
            print(f"Docker image not found: {image}")
            return 1
        except Exception as e:
            print(f"Error running Docker container: {e}")
            return 1


def detect_environment() -> dict:
    """Detect the current execution environment.

    Returns:
        dict: Environment information with keys: is_docker, is_ci, platform, python_version
    """
    return {
        "is_docker": os.path.exists("/.dockerenv"),
        "is_ci": os.environ.get("CI", "false").lower() == "true",
        "platform": os.name,
        "python_version": ".".join(map(str, sys.version_info[:3])),
    }
