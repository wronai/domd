"""Module for testing commands in Docker containers."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class DockerTester:
    """Class for testing commands in Docker containers."""

    def __init__(self, config_path: str = ".dodocker"):
        """Initialize the DockerTester with configuration.

        Args:
            config_path: Path to the .dodocker configuration file.
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.temp_dir = tempfile.mkdtemp(prefix="domd_docker_test_")

    def _load_config(self) -> Dict:
        """Load the .dodocker configuration file.

        Returns:
            Dictionary containing the Docker configuration.
        """
        if not os.path.exists(self.config_path):
            return {}

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def _get_docker_config(self, command: str) -> Dict:
        """Get Docker configuration for a specific command.

        Args:
            command: The command to get configuration for.

        Returns:
            Dictionary with Docker configuration for the command.
        """
        for pattern, config in self.config.items():
            if command.startswith(pattern):
                return config
        return {}

    def test_command_in_docker(self, command: str) -> Tuple[bool, str]:
        """Test a command in a Docker container.

        Args:
            command: The command to test.

        Returns:
            Tuple of (success, output) where success is a boolean indicating
            if the command executed successfully, and output is the command output.
        """
        config = self._get_docker_config(command)
        image = config.get("image", "python:3.9-slim")
        workdir = config.get("workdir", "/app")

        # Create a temporary file with the command
        script_path = os.path.join(self.temp_dir, "test_command.sh")
        with open(script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("set -e\n")
            f.write(f"cd {workdir}\n")
            f.write(f"{command}\n")

        # Make the script executable
        os.chmod(script_path, 0o755)

        # Build Docker command
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{script_path}:/test_command.sh:ro",
            "--entrypoint",
            "/bin/bash",
            image,
            "/test_command.sh",
        ]

        # Add environment variables
        for key, value in config.get("environment", {}).items():
            docker_cmd.insert(2, "-e")
            docker_cmd.insert(3, f"{key}={value}")

        # Add volume mounts
        for host_path, container_path in config.get("volumes", {}).items():
            docker_cmd.insert(2, "-v")
            docker_cmd.insert(3, f"{host_path}:{container_path}")

        # Run the command in Docker
        try:
            result = subprocess.run(
                docker_cmd, capture_output=True, text=True, check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr or str(e)
        except Exception as e:
            return False, str(e)


def test_commands_in_docker(
    commands: List[str], dodocker_path: str = ".dodocker"
) -> Dict[str, Tuple[bool, str]]:
    """Test multiple commands in Docker.

    Args:
        commands: List of commands to test.
        dodocker_path: Path to the .dodocker configuration file.

    Returns:
        Dictionary mapping commands to (success, output) tuples.
    """
    tester = DockerTester(dodocker_path)
    results = {}

    for cmd in commands:
        success, output = tester.test_command_in_docker(cmd)
        results[cmd] = (success, output)

    return results


def update_doignore(
    failed_commands: List[str], doignore_path: str = ".doignore"
) -> None:
    """Update .doignore with failed commands.

    Args:
        failed_commands: List of commands that failed in Docker.
        doignore_path: Path to the .doignore file.
    """
    if not failed_commands:
        return

    # Read existing .doignore
    existing = set()
    if os.path.exists(doignore_path):
        with open(doignore_path, "r") as f:
            existing = {line.strip() for line in f if line.strip()}

    # Add new failed commands
    new_entries = set(failed_commands) - existing
    if not new_entries:
        return

    # Write back to .doignore
    with open(doignore_path, "a") as f:
        f.write("\n# Commands that failed in Docker testing\n")
        for cmd in sorted(new_entries):
            f.write(f"{cmd}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m domd.core.command_detection.docker_tester <command1> [command2 ...]"
        )
        sys.exit(1)

    commands = sys.argv[1:]
    results = test_commands_in_docker(commands)

    failed = []
    for cmd, (success, output) in results.items():
        status = "\033[92mPASS\033[0m" if success else "\033[91mFAIL\033[0m"
        print(f"{status}: {cmd}")
        if not success:
            print(f"  Error: {output}")
            failed.append(cmd)

    if failed:
        update_doignore(failed)
        print(f"\nAdded {len(failed)} failed commands to .doignore")
    else:
        print("\nAll commands passed!")
