"""Parser for Dockerfile files."""

import re
from pathlib import Path
from typing import List

from domd.core.commands import Command
from domd.core.parsing.base import BaseParser


class DockerfileParser(BaseParser):
    """Parser for Dockerfile files."""

    # Class variable for supported file patterns
    supported_file_patterns = [
        "Dockerfile",
        "Dockerfile.*",
        "**/Dockerfile",
        "**/Dockerfile.*",
    ]

    def _extract_image_name(self, file_path: Path) -> str:
        """Extract a default image name from the Dockerfile path.

        Args:
            file_path: Path to the Dockerfile.

        Returns:
            Default image name based on the parent directory name.
        """
        # Default to 'app' if we can't determine a better name
        default_name = "app"

        # Try to get the parent directory name as the image name
        parent_dir = file_path.parent.name
        if parent_dir and parent_dir != ".":
            # Clean up the directory name to be a valid image name
            clean_name = re.sub(r"[^a-z0-9]", "-", parent_dir.lower())
            clean_name = re.sub(r"-+", "-", clean_name).strip("-")
            return clean_name or default_name

        return default_name

    def _extract_exposed_ports(self, content: str) -> List[str]:
        """Extract exposed ports from Dockerfile content.

        Args:
            content: Content of the Dockerfile.

        Returns:
            List of exposed ports as strings.
        """
        # Match EXPOSE directives, handling both space-separated and multiple EXPOSE lines
        expose_matches = re.findall(
            r"^\s*EXPOSE\s+([0-9\s]+)", content, re.MULTILINE | re.IGNORECASE
        )
        if not expose_matches:
            return []

        # Split each match on whitespace and flatten the list
        ports = []
        for match in expose_matches:
            ports.extend(port.strip() for port in match.split() if port.strip())

        return ports

    def _parse_commands(self, content: str) -> List[Command]:
        """Parse Dockerfile content and extract commands.

        Args:
            content: Content of the Dockerfile.

        Returns:
            List of Command objects.
        """
        if not self.file_path:
            return []

        commands = []
        image_name = self._extract_image_name(self.file_path)
        exposed_ports = self._extract_exposed_ports(content)

        # Default port mapping if no ports are exposed
        port_mapping = "-p 80:80"
        if exposed_ports:
            # Use the first exposed port for the default mapping
            port = exposed_ports[0]
            port_mapping = f"-p {port}:{port}"

            # If port 80 is exposed, prefer it for the default mapping
            if "80" in exposed_ports:
                port_mapping = "-p 80:80"

        # Add build command
        build_cmd = f"docker build -t {image_name} ."
        commands.append(
            Command(
                command=build_cmd,
                type="docker_build",
                description=f"Docker: Build {image_name} image",
                source=str(self.file_path),
            )
        )

        # Add run command if we have exposed ports
        run_cmd = f"docker run {port_mapping} {image_name}"
        commands.append(
            Command(
                command=run_cmd,
                type="docker_run",
                description=f"Docker: Run {image_name} container",
                source=str(self.file_path),
            )
        )

        return commands

    def parse(self, content: str = None) -> List[Command]:
        """Parse a Dockerfile and return a list of commands.

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
            except Exception as e:
                logger.error(f"Error reading Dockerfile {self.file_path}: {e}")
                return []

        try:
            return self._parse_commands(content)
        except Exception as e:
            logger.error(f"Error parsing Dockerfile {self.file_path or 'content'}: {e}")
            return []

            # Add run command with port mapping
            run_cmd = f"docker run --rm {port_mapping} {image_name}"
            commands.append(
                Command(
                    command=run_cmd,
                    type="docker_run",
                    description=f"Docker: Run {image_name} container",
                    source=str(self.file_path),
                )
            )

            # Add additional port mappings if multiple ports are exposed
            if len(exposed_ports) > 1:
                for port in exposed_ports[
                    1:
                ]:  # Skip the first port as it's already used
                    if port != "80":  # Skip if it's the same as the default
                        port_cmd = f"docker run --rm -p {port}:{port} {image_name}"
                        commands.append(
                            Command(
                                command=port_cmd,
                                type="docker_run",
                                description=f"Docker: Run {image_name} on port {port}",
                                source=str(self.file_path),
                            )
                        )

            # Add build and run in one command
            build_run_cmd = f"{build_cmd} && {run_cmd}"
            commands.append(
                Command(
                    command=build_run_cmd,
                    type="docker_build_run",
                    description=f"Docker: Build and run {image_name}",
                    source=str(self.file_path),
                )
            )

        except OSError:
            # Log error or handle as needed
            pass

        return commands
