"""Parser for docker-compose.yml files."""

import logging
from typing import List

import yaml

from domd.core.commands import Command
from domd.core.parsing.base import BaseParser

logger = logging.getLogger(__name__)


class DockerComposeParser(BaseParser):
    """Parser for docker-compose.yml files."""

    # Class variable for supported file patterns
    supported_file_patterns = ["docker-compose.yml", "docker-compose.yaml"]

    def _parse_commands(self, content: str) -> List[Command]:
        """Parse docker-compose.yml content and extract commands.

        Args:
            content: Content of the docker-compose.yml file.

        Returns:
            List of Command objects.
        """
        commands = []
        if not self.file_path:
            return commands

        try:
            data = yaml.safe_load(content) or {}

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
                        type=cmd_type,
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

        except yaml.YAMLError as e:
            logger.error(f"Error parsing docker-compose.yml {self.file_path}: {e}")

        return commands

    def parse(self, content: str = None) -> List[Command]:
        """Parse a docker-compose.yml file and return a list of commands.

        Args:
            content: Optional content to parse. If not provided, reads from file_path.

        Returns:
            List of Command objects.
        """
        if content is None:
            if not self.file_path or not self.file_path.exists():
                return []
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError as e:
                logger.error(f"Error reading docker-compose.yml {self.file_path}: {e}")
                return []

        try:
            return self._parse_commands(content)
        except Exception as e:
            logger.error(
                f"Error parsing docker-compose.yml {self.file_path or 'content'}: {e}"
            )
            return []
