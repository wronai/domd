"""Command execution with Docker support."""
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union

from ..utils.environment import EnvironmentDetector


class CommandExecutor:
    """Handles command execution with Docker support."""

    def __init__(self, project_root: Union[str, Path] = "."):
        """Initialize the command executor.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.env_detector = EnvironmentDetector(project_root)

    def execute(
        self,
        command: str,
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        use_docker: Optional[bool] = None,
        docker_image: str = "python:3.9-slim",
    ) -> int:
        """Execute a command, optionally in Docker.

        Args:
            command: Command to execute
            cwd: Working directory for the command
            env: Environment variables
            use_docker: Force Docker usage (None for auto-detect)
            docker_image: Docker image to use if running in Docker

        Returns:
            int: Exit code of the command
        """
        cwd = Path(cwd or self.project_root).resolve()
        env = env or os.environ.copy()

        # Determine if we should use Docker
        if use_docker is None:
            use_docker = self.env_detector.should_use_docker(command)

        if use_docker:
            return self._execute_in_docker(
                command=command, cwd=cwd, env=env, image=docker_image
            )
        return self._execute_locally(command=command, cwd=cwd, env=env)

    def _execute_locally(self, command: str, cwd: Path, env: Dict[str, str]) -> int:
        """Execute a command locally.

        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables

        Returns:
            int: Exit code
        """
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Stream output in real-time
            if process.stdout:
                for line in process.stdout:
                    print(line, end="")

            return process.wait()

        except Exception as e:
            print(f"Error executing command: {e}")
            return 1

    def _execute_in_docker(
        self,
        command: str,
        cwd: Path,
        env: Dict[str, str],
        image: str = "python:3.9-slim",
    ) -> int:
        """Execute a command in a Docker container.

        Args:
            command: Command to execute
            cwd: Working directory (will be mounted to /app in container)
            env: Environment variables
            image: Docker image to use

        Returns:
            int: Exit code from the container
        """
        # Create volume mapping
        volumes = {str(cwd): {"bind": "/app", "mode": "rw"}}

        # Convert environment dict to format expected by docker-py
        env_vars = {k: str(v) for k, v in env.items()}

        return self.env_detector.execute_in_docker(
            command=command,
            image=image,
            volumes=volumes,
            environment=env_vars,
            workdir="/app",
        )
