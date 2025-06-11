"""Environment detection for command execution."""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Common commands that typically require Docker
DOCKER_COMMANDS = {
    "docker",
    "docker-compose",
    "kubectl",
    "helm",
    "ansible-playbook",
    "terraform",
    "packer",
    "vagrant",
    "minikube",
    "kind",
    "k3s",
    "k3d",
    "docker-machine",
    "docker-swarm",
    "docker-stack",
    "docker-service",
}

# Commands that indicate a specific environment is required
ENV_SPECIFIC_COMMANDS = {
    "npm",
    "yarn",
    "pnpm",  # Node.js
    "python",
    "python3",
    "pip",
    "pip3",
    "poetry",  # Python
    "ruby",
    "bundle",
    "gem",
    "rake",  # Ruby
    "go",
    "gofmt",
    "goimports",  # Go
    "cargo",
    "rustc",
    "rustup",  # Rust
    "java",
    "javac",
    "mvn",
    "gradle",  # Java
    "dotnet",
    "nuget",  # .NET
    "php",
    "composer",  # PHP
    "node",
    "npx",  # Node.js
    "aws",
    "gcloud",
    "az",  # Cloud CLIs
    "git",
    "hg",
    "svn",  # Version control
}

# Commands that are typically available in most environments
UNIVERSAL_COMMANDS = {
    "ls",
    "cd",
    "pwd",
    "echo",
    "cat",
    "grep",
    "find",
    "mkdir",
    "rm",
    "cp",
    "mv",
    "chmod",
    "chown",
    "touch",
    "head",
    "tail",
    "less",
    "more",
}


class EnvironmentDetector:
    """Detects if a command should run in a Docker container."""

    @staticmethod
    def should_run_in_docker(command: str, args: List[str] = None) -> Tuple[bool, str]:
        """Determine if a command should run in Docker.

        Args:
            command: The command to check
            args: Command arguments (optional)

        Returns:
            Tuple of (should_run_in_docker: bool, reason: str)
        """
        # Check if command is explicitly marked for Docker
        if command.startswith("docker:"):
            return True, "Explicitly marked with 'docker:' prefix"

        # Check if command is in our known Docker commands
        if command in DOCKER_COMMANDS:
            return True, f"Command '{command}' is known to require Docker"

        # Check if command is not found locally but is environment-specific
        if not shutil.which(command):
            if command in ENV_SPECIFIC_COMMANDS:
                return (
                    True,
                    f"Command '{command}' not found locally but is environment-specific",
                )
            if command not in UNIVERSAL_COMMANDS:
                logger.warning(
                    "Command '%s' not found locally but not in known environment commands",
                    command,
                )

        # Check for Docker-related arguments
        if args:
            if any(arg.startswith(("--docker", "-d")) for arg in args):
                return True, "Docker flag detected in arguments"
            if any("docker" in arg.lower() for arg in args):
                return True, "Docker reference detected in arguments"

        return False, "No Docker requirement detected"

    @staticmethod
    def detect_environment_requirements(command: str, args: List[str] = None) -> Dict:
        """Detect environment requirements for a command.

        Args:
            command: The command to check
            args: Command arguments (optional)

        Returns:
            Dict with environment requirements
        """
        requirements = {
            "needs_docker": False,
            "docker_image": None,
            "reason": "No special requirements",
            "detected_environment": None,
        }

        # Check for Docker requirements
        needs_docker, reason = EnvironmentDetector.should_run_in_docker(command, args)
        if needs_docker:
            requirements.update(
                {
                    "needs_docker": True,
                    "reason": reason,
                    "docker_image": "python:3.11-slim",  # Default image
                }
            )

            # Try to detect more specific image based on command
            if command in {"npm", "yarn", "node", "npx"}:
                requirements["docker_image"] = "node:18"
            elif command in {"python", "pip", "python3", "pip3"}:
                requirements["docker_image"] = "python:3.11-slim"
            elif command in {"ruby", "bundle", "gem"}:
                requirements["docker_image"] = "ruby:3.2"
            elif command in {"java", "javac", "mvn", "gradle"}:
                requirements["docker_image"] = "openjdk:17"

        return requirements
