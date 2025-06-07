"""Parser for docker-compose.yml files."""

from typing import List

import yaml

from ..commands import Command
from .base import BaseParser


class DockerComposeParser(BaseParser):
    """Parser for docker-compose.yml files."""

    @property
    def supported_file_patterns(self) -> List[str]:
        return ["docker-compose.yml", "docker-compose.yaml"]

    def parse(self) -> List[Command]:
        """Parse a docker-compose.yml file and return a list of commands.

        Returns:
            List of Command objects.
        """
        commands = []
        if not self.file_path:
            return commands

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Add basic docker-compose commands
            base_commands = [
                ("up -d", "docker_compose", "Start containers in detached mode"),
                ("down", "docker_compose", "Stop and remove containers"),
                ("build", "docker_compose", "Build or rebuild services"),
                ("up --build -d", "docker_compose", "Rebuild and start containers"),
                ("logs -f", "docker_compose", "Follow log output"),
                ("ps", "docker_compose", "List containers"),
                ("exec web sh", "docker_compose", "Open shell in web service"),
            ]

            for cmd, cmd_type, description in base_commands:
                commands.append(
                    Command(
                        command=f"docker-compose {cmd}",
                        type=cmd_type,  # Using consistent type for all docker-compose commands
                        description=f"Docker Compose: {description}",
                        source=str(self.file_path),
                    )
                )

            # Add service-specific commands if services are defined
            services = data.get("services", {})
            for service_name in services:
                commands.append(
                    Command(
                        command=f"docker-compose logs -f {service_name}",
                        type="docker_compose",
                        description=f"Docker Compose: Logs for {service_name}",
                        source=str(self.file_path),
                    )
                )
                commands.append(
                    Command(
                        command=f"docker-compose exec {service_name} sh",
                        type="docker_compose",
                        description=f"Docker Compose: Shell in {service_name}",
                        source=str(self.file_path),
                    )
                )

        except (yaml.YAMLError, OSError):
            # Log error or handle as needed
            pass

        return commands
