"""Parser for Ansible playbook files."""

from pathlib import Path
from typing import TYPE_CHECKING, List

import yaml

from .base import BaseParser

if TYPE_CHECKING:
    from ..commands import Command


class AnsiblePlaybookParser(BaseParser):
    """Parser for Ansible playbook files."""

    @property
    def supported_file_patterns(self) -> List[str]:
        """Return supported file patterns for Ansible playbooks."""
        return [
            "**/playbooks/*.yml",
            "**/playbooks/*.yaml",
            "**/*playbook*.yml",
            "**/*playbook*.yaml",
            "site.yml",
            "site.yaml",
        ]

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if the file is an Ansible playbook."""
        if not file_path.suffix.lower() in [".yml", ".yaml"]:
            return False

        try:
            with open(file_path, "r") as f:
                content = yaml.safe_load(f)
                # Check if it looks like an Ansible playbook
                if isinstance(content, list) and content and "hosts" in content[0]:
                    return True
        except (yaml.YAMLError, UnicodeDecodeError):
            pass

        return False

    def parse(self, content: str = None) -> "List[Command]":
        """Parse Ansible playbook and extract commands.

        Args:
            content: Optional content of the file to parse. If not provided, will read from file_path.

        Returns:
            List of Command objects
        """
        from domd.core.commands import Command

        if not hasattr(self, "file_path") or self.file_path is None:
            return []

        self._commands: List[Command] = []

        # If content is not provided, read from file
        if (
            content is None
            and hasattr(self, "file_path")
            and not self.file_path.is_dir()
        ):
            try:
                with open(str(self.file_path), "r", encoding="utf-8") as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                # If we can't read the file, return empty list
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Error reading file {self.file_path}: {e}")
                return []

        try:
            playbook = yaml.safe_load(content) if content else []

            if not isinstance(playbook, list):
                return []

            # Get relative path if file is in project directory, otherwise use full path
            playbook_path = str(self.file_path)
            if hasattr(self, "project_root") and self.project_root:
                try:
                    playbook_path = str(self.file_path.relative_to(self.project_root))
                except ValueError:
                    pass

            for play in playbook:
                if not isinstance(play, dict):
                    continue

                play_name = play.get("name", "Unnamed play")
                hosts = play.get("hosts", "all")

                # Create a command to run this playbook
                cmd = f"ansible-playbook {playbook_path}"
                description = f"Ansible playbook: {play_name} (hosts: {hosts})"

                self._commands.append(
                    Command(
                        command=cmd,
                        description=description,
                        type="ansible_playbook",
                        source=str(self.file_path),
                        metadata={
                            "play_name": play_name,
                            "hosts": hosts,
                            "file": str(self.file_path.relative_to(self.project_root)),
                        },
                    )
                )

        except (yaml.YAMLError, UnicodeDecodeError) as e:
            print(f"Error parsing {self.file_path}: {e}")
            return []

        return self._commands
