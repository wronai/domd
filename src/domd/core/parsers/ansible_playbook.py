"""Parser for Ansible playbook files."""

import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

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

    def parse(self) -> "List[Command]":
        """Parse Ansible playbook and extract commands.

        Returns:
            List of Command objects
        """
        from domd.core.commands import Command

        if not self.file_path or not self.file_path.exists():
            return []

        self._commands: List[Command] = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                playbook = yaml.safe_load(f)

            if not isinstance(playbook, list):
                return []

            for play in playbook:
                if not isinstance(play, dict):
                    continue

                play_name = play.get("name", "Unnamed play")
                hosts = play.get("hosts", "all")

                # Create a command to run this playbook
                cmd = (
                    f"ansible-playbook {self.file_path.relative_to(self.project_root)}"
                )
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
